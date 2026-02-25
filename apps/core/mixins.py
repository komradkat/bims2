from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
from django.contrib import messages


class NonBootstrapRequiredMixin(UserPassesTestMixin):
    """
    Mixin that restricts access to bootstrap accounts.
    Bootstrap accounts are intended for initial setup and user management only.
    """

    def test_func(self):
        return self.request.user.is_authenticated and not self.request.user.is_bootstrap

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()

        messages.error(
            self.request,
            "This function is disabled for bootstrapping accounts. Please create and use an official account.",
        )
        return redirect("core:dashboard")
