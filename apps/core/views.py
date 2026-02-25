import threading
import base64
import mimetypes
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import TemplateView, View, ListView, CreateView, UpdateView
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.contrib.auth.forms import PasswordChangeForm
from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.urls import reverse_lazy
from django.contrib import messages
from django.core.cache import cache
from django.db.models import Sum, Q, Count
from django.utils import timezone
from datetime import timedelta
import json
from django.utils.decorators import method_decorator
from .decorators import role_required, tier_required
from .models import Notification, User, BarangayOfficial

# Import models for Dashboard
from apps.residents.models import Resident
from apps.certificates.models import Certificate
from apps.blotter.models import BlotterCase, Hearing
from apps.business.models import BusinessClearance, BusinessPermit
from apps.finance.models import OfficialReceipt


# Custom Login
class CustomLoginView(LoginView):
    template_name = "auth/login.html"
    redirect_authenticated_user = True

    def form_valid(self, form):
        remember_me = self.request.POST.get("remember_me")
        response = super().form_valid(form)
        if not remember_me:
            # Session expires when the browser is closed
            self.request.session.set_expiry(0)
        return response

    def get_success_url(self):
        return reverse_lazy("core:dashboard")


@method_decorator(role_required(["admin"]), name="dispatch")
class UserListView(LoginRequiredMixin, ListView):
    model = User
    template_name = "auth/user_list.html"
    context_object_name = "users"
    paginate_by = 20
    ordering = ["id"]


@method_decorator(role_required(["admin"]), name="dispatch")
class UserCreateView(LoginRequiredMixin, CreateView):
    model = User
    template_name = "auth/user_form.html"
    fields = [
        "username",
        "first_name",
        "last_name",
        "email",
        "role",
        "barangay_position",
        "official",
        "is_active",
    ]
    success_url = reverse_lazy("core:user_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["action"] = "Add"

        # Get requested official ID (if any) from GET parameter
        official_id = self.request.GET.get("official_id")

        # Show all officials in serialized data to ensure auto-population works even if
        # the official doesn't meet filter criteria (e.g. inactive)
        all_officials = BarangayOfficial.objects.all()
        # For the dropdown, we want unlinked ones, BUT always include the specifically requested one
        q = Q(user_account__isnull=True)
        if official_id:
            try:
                q |= Q(id=int(official_id))
            except (ValueError, TypeError):
                pass

        context["officials"] = all_officials.filter(q)

        # Serialize ALL for Alpine.js so we can ALWAYS auto-populate if an ID is passed
        officials_data = {
            str(off.id): {
                "first_name": off.first_name,
                "last_name": off.last_name,
                "email": off.email,
                "position": off.get_position_display(),
            }
            for off in all_officials
        }
        context["officials_json"] = json.dumps(officials_data)

        if official_id:
            context["preselected_official_id"] = str(official_id)

        return context

    def form_valid(self, form):
        user = form.save(commit=False)
        password = self.request.POST.get("password")
        if password:
            user.set_password(password)

        # Link as Bootstrap logic
        link_as_bootstrap = self.request.POST.get("link_as_bootstrap") == "on"
        if link_as_bootstrap and self.request.user.is_bootstrap:
            # Transfer official to current user AND update credentials
            self.request.user.username = user.username
            self.request.user.email = user.email
            self.request.user.official = user.official
            self.request.user.role = user.role
            self.request.user.barangay_position = user.barangay_position
            self.request.user.is_bootstrap = False

            # Sync data from official if linked
            if user.official:
                self.request.user.first_name = user.official.first_name
                self.request.user.last_name = user.official.last_name
                self.request.user.email = user.official.email
                self.request.user.barangay_position = (
                    user.official.get_position_display()
                )

            if password:
                self.request.user.set_password(password)

            self.request.user.save()

            # Update session hash to prevent logout
            update_session_auth_hash(self.request, self.request.user)

            messages.success(
                self.request,
                f"Account '{self.request.user.username}' successfully linked to Official: {self.request.user.official.full_name}. You are no longer in bootstrap mode.",
            )
            return redirect("core:profile")

        # Sync data from official if linked and fields were left empty
        if user.official:
            if not user.first_name:
                user.first_name = user.official.first_name
            if not user.last_name:
                user.last_name = user.official.last_name
            if not user.email:
                user.email = user.official.email
            if not user.barangay_position:
                user.barangay_position = user.official.get_position_display()

        user.save()
        messages.success(self.request, f"User {user.username} created successfully.")
        self.object = user
        return HttpResponseRedirect(self.get_success_url())


@method_decorator(role_required(["admin"]), name="dispatch")
class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = "auth/user_form.html"
    fields = [
        "username",
        "first_name",
        "last_name",
        "email",
        "role",
        "barangay_position",
        "official",
        "is_active",
    ]
    success_url = reverse_lazy("core:user_list")

    def form_valid(self, form):
        user = form.save(commit=False)

        # Sync data from official if linked and fields were left empty (or locked)
        if user.official:
            if not user.first_name:
                user.first_name = user.official.first_name
            if not user.last_name:
                user.last_name = user.official.last_name
            if not user.email:
                user.email = user.official.email
            if not user.barangay_position:
                user.barangay_position = user.official.get_position_display()

        user.save()
        messages.success(self.request, f"User {user.username} updated successfully.")
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["action"] = "Edit"

        all_officials = BarangayOfficial.objects.all()
        # Show all officials but prioritize the currently linked one
        eligible_officials = all_officials.filter(
            Q(user_account__isnull=True) | Q(user_account=self.object)
        )
        context["officials"] = eligible_officials

        # Serialize ALL for Alpine.js auto-population
        officials_data = {
            str(off.id): {
                "first_name": off.first_name,
                "last_name": off.last_name,
                "email": off.email,
                "position": off.get_position_display(),
            }
            for off in all_officials
        }
        context["officials_json"] = json.dumps(officials_data)

        if self.object.official:
            context["preselected_official_id"] = str(self.object.official.id)

        return context


class DashboardView(LoginRequiredMixin, TemplateView):
    """Dashboard view with real data"""

    template_name = "pages/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        this_month_start = today.replace(day=1)

        # ── Residents ────────────────────────────────────────────────
        residents_qs = Resident.objects.filter(is_active=True)
        total_residents = residents_qs.count()
        male_count = residents_qs.filter(sex="M").count()
        female_count = residents_qs.filter(sex="F").count()
        senior_count = residents_qs.filter(is_senior_citizen=True).count()
        pwd_count = residents_qs.filter(is_pwd=True).count()
        fourps_count = residents_qs.filter(is_4ps=True).count()
        solo_parent_count = residents_qs.filter(is_solo_parent=True).count()
        voter_count = residents_qs.filter(is_voter=True).count()
        new_this_month = residents_qs.filter(
            created_at__date__gte=this_month_start
        ).count()

        # ── Certificates ─────────────────────────────────────────────
        total_certs = Certificate.objects.count()
        issued_certs = Certificate.objects.filter(status="issued").count()
        pending_certs = Certificate.objects.filter(status="pending").count()
        certs_this_month = Certificate.objects.filter(
            created_at__date__gte=this_month_start
        ).count()
        cert_by_type = list(
            Certificate.objects.values("certificate_type__name")
            .annotate(count=Count("id"))
            .order_by("-count")
        )
        recent_certs = Certificate.objects.select_related(
            "resident", "certificate_type"
        ).order_by("-created_at")[:6]

        # ── Blotter ──────────────────────────────────────────────────
        total_cases = BlotterCase.objects.count()
        active_cases = BlotterCase.objects.exclude(
            status__in=["settled", "dismissed", "cfa"]
        ).count()
        pending_cases = BlotterCase.objects.filter(status="pending").count()
        ongoing_cases = BlotterCase.objects.filter(status="ongoing").count()
        settled_cases = BlotterCase.objects.filter(status="settled").count()
        dismissed_cases = BlotterCase.objects.filter(status="dismissed").count()
        upcoming_hearings = (
            Hearing.objects.filter(
                scheduled_at__date__gte=today,
                scheduled_at__date__lte=today + timedelta(days=7),
                status="scheduled",
            )
            .select_related("case")
            .order_by("scheduled_at")[:5]
        )

        # ── Business ─────────────────────────────────────────────────
        license_tier = getattr(self.request, "license", {}).get("tier", "community")
        total_permits = BusinessPermit.objects.count()
        active_permits = BusinessPermit.objects.filter(status="active").count()
        pending_permits = BusinessPermit.objects.filter(status="pending").count()
        expired_permits = BusinessPermit.objects.filter(status="expired").count()
        recent_permits = BusinessPermit.objects.order_by("-created_at")[:5]

        # ── Finance ──────────────────────────────────────────────────
        total_revenue = 0
        ytd_receipts = 0
        if license_tier in ["pro", "ultra"]:
            revenue_or = (
                OfficialReceipt.objects.filter(status="paid").aggregate(
                    s=Sum("amount")
                )["s"]
                or 0
            )
            revenue_biz = (
                BusinessClearance.objects.aggregate(s=Sum("amount_paid"))["s"] or 0
            )
            revenue_cert = (
                Certificate.objects.filter(status="paid").aggregate(
                    s=Sum("amount_paid")
                )["s"]
                or 0
            )
            total_revenue = revenue_or + revenue_biz + revenue_cert
            ytd_receipts = OfficialReceipt.objects.filter(
                status="paid", date__year=today.year
            ).count()

        # ── Recent System Activity ────────────────────────────────────
        from apps.audit.models import SystemLog

        recent_logs = SystemLog.objects.select_related("user").order_by("-timestamp")[
            :8
        ]

        # ── Upcoming hearings for dashboard ──────────────────────────
        upcoming_cases_ctx = [
            {
                "color": "error" if h.scheduled_at.date() == today else "warning",
                "number": h.case.case_number,
                "type": h.case.get_incident_type_display(),
                "date": h.scheduled_at,
                "today": h.scheduled_at.date() == today,
            }
            for h in upcoming_hearings
        ]

        # ── Build context ─────────────────────────────────────────────
        context.update(
            {
                # Resident stats
                "total_residents": total_residents,
                "male_count": male_count,
                "female_count": female_count,
                "senior_count": senior_count,
                "pwd_count": pwd_count,
                "fourps_count": fourps_count,
                "solo_parent_count": solo_parent_count,
                "voter_count": voter_count,
                "new_this_month": new_this_month,
                # Certificate stats
                "total_certs": total_certs,
                "issued_certs": issued_certs,
                "pending_certs": pending_certs,
                "certs_this_month": certs_this_month,
                "cert_by_type": cert_by_type,
                "recent_certs": recent_certs,
                # Blotter stats
                "total_cases": total_cases,
                "active_cases": active_cases,
                "pending_cases": pending_cases,
                "ongoing_cases": ongoing_cases,
                "settled_cases": settled_cases,
                "dismissed_cases": dismissed_cases,
                "upcoming_cases": upcoming_cases_ctx,
                # Business stats
                "total_permits": total_permits,
                "active_permits": active_permits,
                "pending_permits": pending_permits,
                "expired_permits": expired_permits,
                "recent_permits": recent_permits,
                # Finance
                "total_revenue": total_revenue,
                "ytd_receipts": ytd_receipts,
                # Activity
                "recent_logs": recent_logs,
                # Convenience
                "today": today,
            }
        )
        return context


@method_decorator(role_required(["admin"]), name="dispatch")
class SettingsView(LoginRequiredMixin, View):
    """View to manage Barangay Information and System Settings"""

    template_name = "core/settings.html"

    def get(self, request):
        from apps.core.models import BarangayInfo, BarangayOfficial

        info = BarangayInfo.objects.first()
        captain = BarangayOfficial.objects.filter(
            position="punong_barangay", is_active=True
        ).first()
        return render(request, self.template_name, {"info": info, "captain": captain})

    def post(self, request):
        from apps.core.models import BarangayInfo

        info = BarangayInfo.objects.first() or BarangayInfo()

        info.name = request.POST.get("barangay_name")
        info.street = request.POST.get("barangay_street", "")
        info.city_municipality = request.POST.get("barangay_city_municipality", "")
        info.province = request.POST.get("barangay_province", "")
        info.region = request.POST.get("region", "")
        info.zip_code = request.POST.get("zip_code", "")
        info.contact_number = request.POST.get("contact_number", "")
        info.email = request.POST.get("barangay_email", "")
        # captain_name & captain_title are auto-synced from the officials roster

        if request.POST.get("latitude"):
            info.latitude = float(request.POST.get("latitude"))
        if request.POST.get("longitude"):
            info.longitude = float(request.POST.get("longitude"))

        if request.FILES.get("barangay_logo"):
            logo = request.FILES["barangay_logo"]
            info.logo = logo
            # Store as Base64 for hardened distribution persistence
            try:
                logo.seek(0)
                logo_data = logo.read()
                info.logo_base64 = base64.b64encode(logo_data).decode("utf-8")
                info.logo_mimetype = mimetypes.guess_type(logo.name)[0] or "image/png"
            except Exception as e:
                print(f"[WARNING] Logo Base64 conversion failed: {e}")

        info.save()

        # Keep the Barangay Hall blip in sync with settings
        try:
            from apps.gis.models import EmergencyService

            hall_defaults = {
                "name": f"{info.name} — Barangay Hall",
                "address": info.full_address or "",
                "contact_number": info.contact_number or "",
                "description": f"Official Barangay Hall of {info.name}.",
                "icon_emoji": "🏛️",
                "is_active": True,
            }
            if info.latitude and info.longitude:
                hall_defaults["latitude"] = info.latitude
                hall_defaults["longitude"] = info.longitude
            EmergencyService.objects.update_or_create(
                service_type="hall",
                defaults=hall_defaults,
            )
        except Exception:
            pass  # Non-fatal

        messages.success(request, "System settings updated successfully.")
        return redirect("core:settings")


@method_decorator(tier_required(["ultra"]), name="dispatch")
class GisMapView(LoginRequiredMixin, TemplateView):
    """GIS Map view (Ultra only)"""

    template_name = "pages/gis/map.html"


class LicenseActivationView(LoginRequiredMixin, View):
    """License activation view for activating license keys"""

    template_name = "auth/license_activation.html"

    def get(self, request):
        from apps.core.utils.hardware import get_hardware_id
        from apps.core.models import LicenseKey

        hardware_id = get_hardware_id()
        current_license = LicenseKey.objects.filter(
            hardware_id=hardware_id, is_active=True
        ).first()

        return render(
            request,
            self.template_name,
            {"hardware_id": hardware_id, "current_license": current_license},
        )

    def post(self, request):
        from apps.core.utils.hardware import get_hardware_id
        from apps.core.models import LicenseKey

        license_key = request.POST.get("license_key", "").strip()
        hardware_id = get_hardware_id()

        if not license_key:
            messages.error(request, "Please enter a license key.")
            return redirect("core:license_activation")

        try:
            # Special Master Bypass Key for Developer Testing (Sanbox/Standalone)
            if license_key == "BIMS2-ULTRA-MASTER-BYPASS-2026":
                license_obj, created = LicenseKey.objects.get_or_create(
                    key=license_key,
                    defaults={
                        "tier": "ultra",
                        "max_users": 999,
                        "is_active": True,
                        "hardware_id": hardware_id,
                    },
                )
                if not created:
                    license_obj.hardware_id = hardware_id
                    license_obj.is_active = True
                    license_obj.save()
            else:
                license_obj = LicenseKey.objects.get(key=license_key)

            # Check if already activated on another machine
            if license_obj.hardware_id and license_obj.hardware_id != hardware_id:
                messages.error(
                    request,
                    "This license is already activated on another server. "
                    "Please contact support to transfer your license.",
                )
                return redirect("core:license_activation")

            # Activate license
            license_obj.hardware_id = hardware_id
            license_obj.is_active = True
            license_obj.save()

            # Clear cache to force reload of license data
            cache.delete("active_license")

            messages.success(
                request,
                f"License activated successfully! Tier: {license_obj.tier.upper()} | "
                f"Max Users: {license_obj.max_users}",
            )
            return redirect("core:dashboard")

        except LicenseKey.DoesNotExist:
            messages.error(request, "Invalid license key. Please check and try again.")
            return redirect("core:license_activation")


class LicenseInfoView(TemplateView):
    """View to display detailed license and hardware information"""

    template_name = "auth/license_info.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "License Information"
        return context


class SetupView(View):
    """
    Initial System Setup Wizard.
    Allows setting Barangay Info and creating/updating the Admin account.
    """

    template_name = "core/setup.html"

    def get(self, request):
        from apps.core.models import BarangayInfo

        # If setup is already complete, redirect to dashboard
        if BarangayInfo.objects.filter(is_setup_complete=True).exists():
            return redirect("core:dashboard")

        return render(request, self.template_name)

    def post(self, request):
        from apps.core.models import BarangayInfo

        User = get_user_model()

        # 1. Barangay Info
        name = request.POST.get("barangay_name")
        street = request.POST.get("barangay_street", "")
        city_municipality = request.POST.get("barangay_city_municipality")
        province = request.POST.get("barangay_province")
        region = request.POST.get("barangay_region", "")
        zip_code = request.POST.get("barangay_zip_code", "")
        contact = request.POST.get("contact_number", "")
        email = request.POST.get("barangay_email", "")

        # New: GIS Coordinates
        latitude = request.POST.get("latitude")
        longitude = request.POST.get("longitude")

        logo = request.FILES.get("barangay_logo")

        # 2. Admin Account
        username = request.POST.get("admin_username")
        password = request.POST.get("admin_password")
        # admin_email = request.POST.get('admin_email') # Removed requirement for separate email in this step

        # Basic Validation
        if not all([name, city_municipality, province, username, password]):
            messages.error(request, "Please fill in all required fields.")
            return render(request, self.template_name)

        try:
            # Save Barangay Info
            # Singleton: Get existing or create new
            info = BarangayInfo.objects.first()
            if not info:
                info = BarangayInfo()

            info.name = name
            info.street = street
            info.city_municipality = city_municipality
            info.province = province
            info.region = region
            info.zip_code = zip_code
            info.contact_number = contact
            info.email = email

            # Save coordinates if provided
            if latitude and longitude:
                try:
                    info.latitude = float(latitude)
                    info.longitude = float(longitude)
                except ValueError:
                    pass  # Ignore invalid floats

            if logo:
                info.logo = logo
                # Store as Base64 for hardened distribution persistence
                try:
                    logo.seek(0)
                    logo_data = logo.read()
                    info.logo_base64 = base64.b64encode(logo_data).decode("utf-8")
                    info.logo_mimetype = (
                        mimetypes.guess_type(logo.name)[0] or "image/png"
                    )
                except Exception as e:
                    print(f"[WARNING] Logo Base64 conversion failed: {e}")

            info.is_setup_complete = True
            info.save()

            # Auto-create / update the Barangay Hall blip
            try:
                from apps.gis.models import EmergencyService

                hall_address = (
                    info.full_address
                    or f"{info.street}, {info.city_municipality}, {info.province}".strip(
                        ", "
                    )
                )
                defaults = {
                    "name": f"{info.name} — Barangay Hall",
                    "address": hall_address,
                    "contact_number": info.contact_number or "",
                    "description": f"Official Barangay Hall of {info.name}.",
                    "icon_emoji": "🏛️",
                    "is_active": True,
                }
                if info.latitude and info.longitude:
                    defaults["latitude"] = info.latitude
                    defaults["longitude"] = info.longitude
                EmergencyService.objects.update_or_create(
                    service_type="hall",
                    defaults=defaults,
                )
            except Exception as _hall_err:
                pass  # Non-fatal; don't block setup completion

            # Save Puroks
            from apps.residents.models import Purok

            purok_names = request.POST.getlist("puroks[]")
            # Clear existing if any (since this is setup, usually empty)
            for p_name in purok_names:
                if p_name.strip():
                    Purok.objects.get_or_create(name=p_name.strip())

            # Create/Update Admin User
            # ... existing admin logic ...
            if User.objects.filter(username=username).exists():
                user = User.objects.get(username=username)
                user.set_password(password)
                # user.email = admin_email
                user.role = "admin"
                user.is_superuser = True
                user.is_staff = True
                user.is_bootstrap = True  # Set is_bootstrap to True
                user.save()
            else:
                User.objects.create_superuser(
                    username=username,
                    # email=admin_email,
                    email="",
                    password=password,
                    role="admin",
                    barangay_position="Administrator",
                    is_bootstrap=True,  # Set is_bootstrap to True
                )

            messages.success(
                request,
                "System Setup Completed Successfully! Initializing your workspace...",
            )
            return redirect("core:initializing")

        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return render(request, self.template_name)


class InitializingView(TemplateView):
    """Premium loading screen for system initialization"""

    template_name = "core/initializing.html"


@method_decorator(role_required(["admin"]), name="dispatch")
class TriggerInitializeAPI(LoginRequiredMixin, View):
    """API endpoint to trigger background initialization tasks (like GIS import)"""

    def post(self, request):
        from django.core.management import call_command
        from django.http import JsonResponse

        def run_initialization():
            try:
                # Trigger the GIS Importer
                # Note: Radius is set to 5km by default
                call_command("import_nearby_services", radius=5000)
            except Exception as e:
                print(f"Initialization background task error: {e}")

        # Run in background thread to avoid blocking the UI
        thread = threading.Thread(target=run_initialization)
        thread.daemon = True
        thread.start()

        return JsonResponse(
            {
                "status": "started",
                "message": "Initialization background tasks triggered.",
            }
        )


# ── Officials ──────────────────────────────────────────────────────────────


class OfficialsListView(LoginRequiredMixin, ListView):
    model = BarangayOfficial
    template_name = "pages/officials/list.html"
    context_object_name = "officials"

    def get_queryset(self):
        return BarangayOfficial.objects.all()


@method_decorator(role_required(["admin"]), name="dispatch")
class OfficialCreateView(LoginRequiredMixin, View):
    template_name = "pages/officials/form.html"

    def get(self, request):
        from apps.core.models import BarangayOfficial as BOf

        return render(
            request,
            self.template_name,
            {
                "position_choices": BOf.POSITION_CHOICES,
                "committee_choices": BOf.COMMITTEE_CHOICES,
                "action": "Add",
            },
        )

    def post(self, request):
        from apps.core.models import BarangayOfficial as BOf

        try:
            official = BOf()
            official.position = request.POST.get("position")
            official.committee = request.POST.get("committee", "")
            official.honorific = request.POST.get("honorific", "")
            official.first_name = request.POST.get("first_name")
            official.middle_name = request.POST.get("middle_name", "")
            official.last_name = request.POST.get("last_name")
            official.suffix = request.POST.get("suffix", "")
            if request.FILES.get("photo"):
                official.photo = request.FILES["photo"]
            official.term_start = request.POST.get("term_start") or None
            official.term_end = request.POST.get("term_end") or None
            official.contact_number = request.POST.get("contact_number", "")
            official.email = request.POST.get("email", "")
            official.is_active = request.POST.get("is_active") == "on"
            official.order = int(request.POST.get("order", 0))
            official.save()

            # If this is Punong Barangay, update captain_name on BarangayInfo
            if official.position == "punong_barangay":
                from apps.core.models import BarangayInfo

                info = BarangayInfo.objects.first()
                if info:
                    info.captain_name = official.display_name.upper()
                    info.save(update_fields=["captain_name"])

            messages.success(request, f"{official.full_name} has been added.")
            return redirect("core:officials")
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
            return render(
                request,
                self.template_name,
                {
                    "position_choices": BOf.POSITION_CHOICES,
                    "committee_choices": BOf.COMMITTEE_CHOICES,
                    "action": "Add",
                },
            )


@method_decorator(role_required(["admin"]), name="dispatch")
class OfficialUpdateView(LoginRequiredMixin, View):
    template_name = "pages/officials/form.html"

    def get(self, request, pk):
        from django.shortcuts import get_object_or_404
        from apps.core.models import BarangayOfficial as BOf

        official = get_object_or_404(BOf, pk=pk)
        return render(
            request,
            self.template_name,
            {
                "official": official,
                "position_choices": BOf.POSITION_CHOICES,
                "committee_choices": BOf.COMMITTEE_CHOICES,
                "action": "Edit",
            },
        )

    def post(self, request, pk):
        from django.shortcuts import get_object_or_404
        from apps.core.models import BarangayOfficial as BOf

        official = get_object_or_404(BOf, pk=pk)
        try:
            official.position = request.POST.get("position")
            official.committee = request.POST.get("committee", "")
            official.honorific = request.POST.get("honorific", "")
            official.first_name = request.POST.get("first_name")
            official.middle_name = request.POST.get("middle_name", "")
            official.last_name = request.POST.get("last_name")
            official.suffix = request.POST.get("suffix", "")
            if request.FILES.get("photo"):
                official.photo = request.FILES["photo"]
            official.term_start = request.POST.get("term_start") or None
            official.term_end = request.POST.get("term_end") or None
            official.contact_number = request.POST.get("contact_number", "")
            official.email = request.POST.get("email", "")
            official.is_active = request.POST.get("is_active") == "on"
            official.order = int(request.POST.get("order", 0))
            official.save()

            if official.position == "punong_barangay":
                from apps.core.models import BarangayInfo

                info = BarangayInfo.objects.first()
                if info:
                    info.captain_name = official.display_name.upper()
                    info.save(update_fields=["captain_name"])

            messages.success(request, f"{official.full_name} has been updated.")
            return redirect("core:officials")
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
            return render(
                request,
                self.template_name,
                {
                    "official": official,
                    "position_choices": BOf.POSITION_CHOICES,
                    "committee_choices": BOf.COMMITTEE_CHOICES,
                    "action": "Edit",
                },
            )


@method_decorator(role_required(["admin"]), name="dispatch")
class OfficialDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        from django.shortcuts import get_object_or_404

        official = get_object_or_404(BarangayOfficial, pk=pk)
        name = official.full_name
        official.delete()
        messages.success(request, f"{name} has been removed.")
        return redirect("core:officials")


# ── Informational Pages ──────────────────────────────────────────────────


class AboutView(TemplateView):
    template_name = "pages/info/about.html"


class PrivacyView(TemplateView):
    template_name = "pages/info/privacy.html"


class TermsView(TemplateView):
    template_name = "pages/info/terms.html"


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "barangay_position"]
        widgets = {
            "first_name": forms.TextInput(
                attrs={"class": "input input-bordered w-full"}
            ),
            "last_name": forms.TextInput(
                attrs={"class": "input input-bordered w-full"}
            ),
            "email": forms.EmailInput(attrs={"class": "input input-bordered w-full"}),
            "barangay_position": forms.TextInput(
                attrs={"class": "input input-bordered w-full"}
            ),
        }


class OfficialProfileForm(forms.ModelForm):
    class Meta:
        model = BarangayOfficial
        fields = ["honorific", "middle_name", "suffix", "contact_number"]
        widgets = {
            "honorific": forms.TextInput(
                attrs={"class": "input input-bordered w-full"}
            ),
            "middle_name": forms.TextInput(
                attrs={"class": "input input-bordered w-full"}
            ),
            "suffix": forms.TextInput(attrs={"class": "input input-bordered w-full"}),
            "contact_number": forms.TextInput(
                attrs={"class": "input input-bordered w-full"}
            ),
        }


class CheckForUpdatesAPI(LoginRequiredMixin, View):
    """API endpoint to check for system updates."""

    def get(self, request):
        from .utils.update import check_for_updates  # To be created
        from django.http import JsonResponse
        from django.conf import settings

        current_version = getattr(settings, "BIMS_VERSION", "1.0.0-alpha")
        update_info = check_for_updates(current_version)

        return JsonResponse(
            {
                "current_version": current_version,
                "latest_version": update_info.get("latest_version"),
                "update_available": update_info.get("update_available"),
                "changelog": update_info.get("changelog", ""),
            }
        )


class ProfileView(LoginRequiredMixin, View):
    template_name = "core/profile.html"

    def get(self, request):
        user_form = ProfileForm(instance=request.user)
        official_form = None
        if request.user.official:
            official_form = OfficialProfileForm(instance=request.user.official)

        return render(
            request,
            self.template_name,
            {"form": user_form, "official_form": official_form},
        )

    def post(self, request):
        if request.user.is_bootstrap:
            messages.error(request, "Bootstrap account settings cannot be modified.")
            return redirect("core:profile")

        user_form = ProfileForm(request.POST, instance=request.user)
        official_form = None
        official_valid = True

        if request.user.official:
            official_form = OfficialProfileForm(
                request.POST, instance=request.user.official
            )
            official_valid = official_form.is_valid()

        if user_form.is_valid() and official_valid:
            user_form.save()
            if official_form:
                official_form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("core:profile")

        return render(
            request,
            self.template_name,
            {"form": user_form, "official_form": official_form},
        )


class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    form_class = PasswordChangeForm
    success_url = reverse_lazy("core:profile")
    template_name = "auth/password_change.html"

    def form_valid(self, form):
        messages.success(self.request, "Your password has been changed successfully.")
        return super().form_valid(form)


class MarkNotificationReadView(LoginRequiredMixin, View):
    def post(self, request, pk):
        from django.shortcuts import get_object_or_404

        notification = get_object_or_404(Notification, pk=pk, user=request.user)
        notification.is_read = True
        notification.save()

        # Return an empty response for HTMX (the item will be removed/updated in the UI)
        return HttpResponse("")


# Error Views
def error_404(request, exception):
    return render(request, "404.html", status=404)


def error_500(request):
    import logging

    logger = logging.getLogger("apps")
    logger.exception("An unhandled 500 error occurred.")
    return render(request, "500.html", status=500)
