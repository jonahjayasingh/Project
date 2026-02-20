from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils.text import slugify
from django.http import HttpResponseForbidden
from .models import Post, Comment
from .utils import is_bullying
from .forms import PostForm

class PostList(generic.ListView):
    queryset = Post.objects.filter(status='published').order_by('-created_on')
    template_name = 'index.html'

def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    # Only get top-level comments (those without parents)
    comments = post.comments.filter(is_removed=False, parent=None)
    
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('login')
            
        content = request.POST.get('content')
        parent_id = request.POST.get('parent_id')
        
        if content:
            if is_bullying(content):
                profile = request.user.userprofile
                profile.comment_warning_count += 1
                if profile.comment_warning_count >= 10:
                    profile.is_blocked = True
                    profile.save()
                    messages.error(request, "Account blocked: 10 violations in comments.")
                    return redirect('home')
                profile.save()
                messages.warning(request, f"Warning: Bullying content detected in comment. ({profile.comment_warning_count}/10)")
                return redirect('post_detail', slug=slug)
            
            parent_obj = None
            if parent_id:
                try:
                    parent_obj = Comment.objects.get(id=parent_id)
                except Comment.DoesNotExist:
                    pass

            Comment.objects.create(
                post=post,
                author=request.user,
                content=content,
                parent=parent_obj
            )
            messages.success(request, "Comment posted successfully!")
            return redirect('post_detail', slug=slug)
            
    return render(request, 'post_detail.html', {'post': post, 'comments': comments})

class AddPostView(LoginRequiredMixin, generic.CreateView):
    model = Post
    form_class = PostForm
    template_name = 'add_post.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        title = form.cleaned_data.get('title')
        content = form.cleaned_data.get('content')
        
        if is_bullying(title) or is_bullying(content):
            profile = self.request.user.userprofile
            profile.post_warning_count += 1
            if profile.post_warning_count >= 5:
                profile.is_blocked = True
                profile.save()
                messages.error(self.request, "Account blocked: 5 violations in posts.")
                return redirect('home')
            profile.save()
            messages.warning(self.request, f"Warning: Bullying content detected in post. ({profile.post_warning_count}/5)")
            return redirect('add_post')

        form.instance.author = self.request.user
        form.instance.slug = slugify(form.instance.title)
        form.instance.status = 'published'
        messages.success(self.request, "Post created successfully!")
        return super().form_valid(form)

class EditPostView(LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'edit_post.html'
    
    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author
    
    def get_success_url(self):
        return reverse_lazy('post_detail', kwargs={'slug': self.object.slug})
    
    def form_valid(self, form):
        title = form.cleaned_data.get('title')
        content = form.cleaned_data.get('content')
        
        if is_bullying(title) or is_bullying(content):
            profile = self.request.user.userprofile
            profile.post_warning_count += 1
            if profile.post_warning_count >= 5:
                profile.is_blocked = True
                profile.save()
                messages.error(self.request, "Account blocked: 5 violations in posts.")
                return redirect('home')
            profile.save()
            messages.warning(self.request, f"Warning: Bullying content detected. ({profile.post_warning_count}/5)")
            return redirect('edit_post', pk=self.object.pk)
        
        form.instance.slug = slugify(form.instance.title)
        messages.success(self.request, "Post updated successfully!")
        return super().form_valid(form)

class DeletePostView(LoginRequiredMixin, UserPassesTestMixin, generic.DeleteView):
    model = Post
    template_name = 'delete_post.html'
    success_url = reverse_lazy('home')
    
    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, "Post deleted successfully!")
        return super().delete(request, *args, **kwargs)

def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    post_slug = comment.post.slug
    
    if request.user != comment.author:
        return HttpResponseForbidden("You don't have permission to delete this comment.")
    
    if request.method == 'POST':
        comment.delete()
        messages.success(request, "Comment deleted successfully!")
        return redirect('post_detail', slug=post_slug)
    
    return render(request, 'delete_comment.html', {'comment': comment})

class RegisterView(generic.CreateView):
    form_class = UserCreationForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response

def blocked_view(request):
    return render(request, 'blocked.html')
