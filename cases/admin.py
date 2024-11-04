from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import Case, VerificationCode, Withdrawal, KYCVerification

class VerificationCodeInline(admin.TabularInline):
    model = VerificationCode
    extra = 3
    max_num = 3
    fields = ('step', 'code', 'is_used', 'expires_at')
    readonly_fields = ('is_used',)

@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'company', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'company')
    inlines = [VerificationCodeInline]
    
    def get_readonly_fields(self, request, obj=None):
        if obj and obj.status == 'completed':
            return ('status',) + self.readonly_fields
        return self.readonly_fields

@admin.register(Withdrawal)
class WithdrawalAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username',)
    readonly_fields = ('created_at',)

    fieldsets = (
        (None, {
            'fields': ('user', 'amount', 'status')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.status == 'completed':
            return self.readonly_fields + ('user', 'amount', 'status')
        return self.readonly_fields

    actions = ['mark_as_completed', 'mark_as_rejected']

    def mark_as_completed(self, request, queryset):
        updated = queryset.update(status='completed')
        self.message_user(request, f'{updated} withdrawals marked as completed.')
    mark_as_completed.short_description = "Mark selected withdrawals as completed"

    def mark_as_rejected(self, request, queryset):
        updated = queryset.update(status='rejected')
        self.message_user(request, f'{updated} withdrawals marked as rejected.')
    mark_as_rejected.short_description = "Mark selected withdrawals as rejected"

@admin.register(KYCVerification)
class KYCVerificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_verified', 'document_type', 'verification_date', 'document_preview')
    list_filter = ('is_verified', 'document_type', 'verification_date')
    search_fields = ('user__username', 'document_number')
    readonly_fields = ('verification_date', 'document_preview_large')

    fieldsets = (
        (None, {
            'fields': ('user', 'is_verified', 'document_type', 'document_number')
        }),
        ('Document', {
            'fields': ('document_image', 'document_preview_large'),
        }),
        ('Verification Details', {
            'fields': ('verification_date',),
            'classes': ('collapse',)
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.is_verified:
            return self.readonly_fields + ('user', 'document_type', 'document_number', 'document_image')
        return self.readonly_fields

    actions = ['mark_as_verified', 'mark_as_unverified']

    def mark_as_verified(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(is_verified=True, verification_date=timezone.now())
        self.message_user(request, f'{updated} KYC verifications marked as verified.')
    mark_as_verified.short_description = "Mark selected KYC verifications as verified"

    def mark_as_unverified(self, request, queryset):
        updated = queryset.update(is_verified=False, verification_date=None)
        self.message_user(request, f'{updated} KYC verifications marked as unverified.')
    mark_as_unverified.short_description = "Mark selected KYC verifications as unverified"

    def document_preview(self, obj):
        if obj.document_image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.document_image.url)
        return "No Image"
    document_preview.short_description = 'Document Preview'

    def document_preview_large(self, obj):
        if obj.document_image:
            return format_html('<img src="{}" width="400" style="max-height: 400px; object-fit: contain;" />', obj.document_image.url)
        return "No Image"
    document_preview_large.short_description = 'Document Preview (Large)'