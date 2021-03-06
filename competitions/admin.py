from django.shortcuts import redirect
from reversion import VersionAdmin

from django.contrib import admin
from django.contrib import messages
from django.core.exceptions import ValidationError

from base.admin import PrettyFilterMixin, RestrictedCompetitionAdminMixin
from base.util import editonly_fieldsets

from .models import (Competition, Season, Series,
                     CompetitionUserRegistration, CompetitionOrgRegistration)


@editonly_fieldsets
class CompetitionAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'organizer_group',
        'site',
        'added_at'
    )

    readonly_fields = ('added_by', 'modified_by', 'added_at', 'modified_at')

    fieldsets = (
        (None, {
            'fields': ('name', 'organizer_group', 'site')
        }),
    )

    editonly_fieldsets = (
        ('Details', {
            'classes': ('grp-collapse', 'grp-closed'),
            'fields': ('added_at', 'modified_at', 'added_by', 'modified_by')
        }),
    )


@editonly_fieldsets
class CompetitionUserRegistrationAdmin(RestrictedCompetitionAdminMixin,
                                       PrettyFilterMixin, VersionAdmin):

    list_display = (
        'user',
        'competition',
        'added_at',
    )

    list_filter = ('competition',)
    search_fields = (
        'user__username',
        'user__first_name',
        'user__last_name',
        'competition__name'
    )

    raw_id_fields = ('user',)

    autocomplete_lookup_fields = {
        'fk': ['user'],
    }

    readonly_fields = ('added_by', 'modified_by', 'added_at', 'modified_at')

    fieldsets = (
        (None, {
            'fields': ('competition', 'user', 'added_at')
        }),
    )

    editonly_fieldsets = (
        ('Details', {
            'classes': ('grp-collapse', 'grp-closed'),
            'fields': ('added_at', 'modified_at', 'added_by', 'modified_by')
        }),
    )


@editonly_fieldsets
class CompetitionOrgRegistrationAdmin(RestrictedCompetitionAdminMixin,
                                      PrettyFilterMixin, VersionAdmin):

    list_display = (
        'organizer',
        'competition',
        'added_at',
        'approved',
    )

    list_filter = ('competition',)

    search_fields = (
        'organizer__username',
        'organizer__first_name',
        'organizer__last_name'
    )

    raw_id_fields = ('organizer',)

    autocomplete_lookup_fields = {
        'fk': ['organizer'],
    }

    readonly_fields = ('added_by', 'modified_by', 'added_at', 'modified_at')

    fieldsets = (
        (None, {
            'fields': ('competition', 'organizer', 'approved')
        }),
    )

    editonly_fieldsets = (
        ('Details', {
            'classes': ('grp-collapse', 'grp-closed'),
            'fields': ('added_at', 'modified_at', 'added_by', 'modified_by')
        }),
    )


@editonly_fieldsets
class SeasonAdmin(RestrictedCompetitionAdminMixin,
                  PrettyFilterMixin, VersionAdmin):

    list_display = (
        'competition',
        'year',
        'name',
        'number',
        'start',
        'end',
        'join_deadline'
    )

    list_filter = (
        'competition',
        'year',
        'join_deadline'
    )

    search_fields = (
        'name',
        'competition__name'
    )

    readonly_fields = ('added_by', 'modified_by', 'added_at', 'modified_at')

    raw_id_fields = ('competition',)

    autocomplete_lookup_fields = {
        'fk': ['competition'],
    }

    fieldsets = (
        (None, {
            'fields': ('competition',
                       'name',
                       'year',
                       'number',
                       'start',
                       'end',
                       'join_deadline',
                       'sum_method',
                       )
        }),
    )

    editonly_fieldsets = (
        ('Details', {
            'classes': ('grp-collapse', 'grp-closed'),
            'fields': ('added_at', 'modified_at', 'added_by', 'modified_by')
        }),
    )


@editonly_fieldsets
class SeriesAdmin(RestrictedCompetitionAdminMixin,
                  PrettyFilterMixin, VersionAdmin):

    competition_field = 'season__competition'

    list_display = (
        'season',
        'name',
        'number',
        'submission_deadline',
        'is_active'
    )

    list_filter = ('season', 'submission_deadline', 'is_active')
    search_fields = (
        'name',
        'season__name'
    )

    readonly_fields = ('added_by', 'modified_by', 'added_at', 'modified_at')

    raw_id_fields = ('season', 'problemset')

    autocomplete_lookup_fields = {
        'fk': ['season' , 'problemset'],
    }

    fieldsets = (
        (None, {
            'fields': ('season', 'name', 'number', 'problemset',
                       'submission_deadline', 'is_active', 'sum_method',
                       'results_note')
        }),
    )

    editonly_fieldsets = (
        ('Details', {
            'classes': ('grp-collapse', 'grp-closed'),
            'fields': ('added_at', 'modified_at', 'added_by', 'modified_by')
        }),
    )

    actions = ['make_active', 'results_to_tex']

    def make_active(self, request, queryset):
        for series in queryset:
            try:
                series.is_active = True
                series.full_clean()
                series.save()
            except ValidationError, e:
                for message in e.messages:
                    self.message_user(request,
                                      message=message,
                                      level=messages.ERROR)
    make_active.short_description = "Make active"

    def results_to_tex(self, request, queryset):
        return redirect('competitions_series_results_tex', queryset[0].pk)

    results_to_tex.short_description = 'Export results to TeX'

# Register to the admin site
admin.site.register(Competition, CompetitionAdmin)
admin.site.register(CompetitionUserRegistration,
                    CompetitionUserRegistrationAdmin)
admin.site.register(CompetitionOrgRegistration,
                    CompetitionOrgRegistrationAdmin)
admin.site.register(Season, SeasonAdmin)
admin.site.register(Series, SeriesAdmin)
