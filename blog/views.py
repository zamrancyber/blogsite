from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponseRedirect
from .models import Post, Comment, Profile, Like
from .forms import CommentForm, ProfileForm

# ---------- Home page – only published posts for regular users ----------
class PostListView(ListView):
    model = Post
    template_name = 'blog/home.html'
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self):
        if self.request.user.is_staff or self.request.user.is_superuser:
            return Post.objects.all().order_by('-date_posted')
        else:
            return Post.objects.filter(status='published').order_by('-date_posted')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            # Get IDs of posts liked by the current user
            liked_posts = Like.objects.filter(user=self.request.user).values_list('post_id', flat=True)
            context['liked_posts'] = set(liked_posts)
        else:
            context['liked_posts'] = set()
        return context

# ---------- Detail page – only show if published OR author/admin ----------
class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'

    def dispatch(self, request, *args, **kwargs):
        post = self.get_object()
        if post.status == 'published' or request.user == post.author or request.user.is_staff:
            return super().dispatch(request, *args, **kwargs)
        else:
            from django.http import Http404
            raise Http404("This post is not available.")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.filter(active=True)
        if self.request.user.is_authenticated:
            context['form'] = CommentForm()
            context['user_liked'] = self.object.likes.filter(user=self.request.user).exists()
        else:
            context['form'] = None
            context['user_liked'] = False
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not request.user.is_authenticated:
            return redirect('login')
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = self.object
            comment.user = request.user
            comment.name = request.user.username
            comment.email = request.user.email or ''
            comment.save()
            return redirect('post-detail', pk=self.object.pk)
        return self.render_to_response(self.get_context_data(form=form))

# ---------- Create new post – always pending ----------
class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'content', 'image']

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.status = 'pending'
        return super().form_valid(form)

# ---------- Update post – only author ----------
class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'content', 'image']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

# ---------- Delete post – only author ----------
class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('blog-home')
    template_name = 'blog/post_confirm_delete.html'

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

# ---------- Edit comment – only comment author ----------
class CommentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment_form.html'

    def get_success_url(self):
        return reverse_lazy('post-detail', kwargs={'pk': self.object.post.pk})

    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.user

# ---------- Delete comment – allow comment author OR post author ----------
class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('post-detail', kwargs={'pk': self.object.post.pk})

    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.user or self.request.user == comment.post.author

# ---------- Like / Unlike a post ----------
@login_required
def like_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    like, created = Like.objects.get_or_create(user=request.user, post=post)
    if not created:
        # Already liked -> unlike
        like.delete()
    # Redirect back to the referring page (either home or post detail)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('post-detail', args=[pk])))

# ---------- Authentication views ----------
def logout_view(request):
    logout(request)
    return redirect('blog-home')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('blog-home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

# ---------- Profile views ----------
def profile_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    profile = profile_user.profile
    posts = profile_user.post_set.filter(status='published').order_by('-date_posted')
    context = {
        'profile_user': profile_user,
        'profile': profile,
        'posts': posts,
    }
    return render(request, 'blog/profile.html', context)

@login_required
def edit_profile(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile', username=request.user.username)
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'blog/edit_profile.html', {'form': form})



from django.http import JsonResponse
from django.db import connections
from django.db.utils import OperationalError

def health_check(request):
    """
    Health check endpoint for monitoring.
    Returns 200 if the application and database are running.
    """
    health_status = {
        "status": "ok",
        "database": "ok"
    }
    status_code = 200

    # Check database connectivity
    try:
        connections['default'].cursor()
    except OperationalError:
        health_status["status"] = "error"
        health_status["database"] = "disconnected"
        status_code = 500
    except Exception:
        health_status["status"] = "error"
        health_status["database"] = "error"
        status_code = 500

    return JsonResponse(health_status, status=status_code)