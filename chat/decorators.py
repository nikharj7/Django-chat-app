from django.shortcuts import redirect

def custom_login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')  # Replace 'login' with your login URL name
        return view_func(request, *args, **kwargs)
    return wrapper
