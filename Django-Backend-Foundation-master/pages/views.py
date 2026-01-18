from django.shortcuts import redirect, render
from django.views import View


class LandingView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect("workspaces:chooser")
        return render(request, "pages/landing.html")
