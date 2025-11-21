# training/admin.py
from django.contrib import admin
from .models import SocialSkillsCourse, CourseLesson, CourseEnrollment, LessonProgress


class CourseLessonInline(admin.TabularInline):
    model = CourseLesson
    extra = 1
    fields = ['title', 'content_type', 'order', 'is_mandatory']


@admin.register(SocialSkillsCourse)
class SocialSkillsCourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'difficulty', 'duration_hours', 'is_active', 'order']
    list_filter = ['category', 'difficulty', 'is_active']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    ordering = ['order', 'title']
    inlines = [CourseLessonInline]


@admin.register(CourseLesson)
class CourseLessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'content_type', 'order', 'is_mandatory']
    list_filter = ['content_type', 'is_mandatory', 'course']
    search_fields = ['title', 'content']
    ordering = ['course', 'order']


@admin.register(CourseEnrollment)
class CourseEnrollmentAdmin(admin.ModelAdmin):
    list_display = ['candidate', 'course', 'status', 'progress_percentage', 'enrolled_at', 'certificate_issued']
    list_filter = ['status', 'certificate_issued', 'enrolled_at']
    search_fields = ['candidate__first_name', 'candidate__last_name', 'course__title']
    readonly_fields = ['enrolled_at', 'started_at', 'completed_at', 'certificate_number']
    ordering = ['-enrolled_at']


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ['enrollment', 'lesson', 'completed', 'completed_at']
    list_filter = ['completed', 'completed_at']
    search_fields = ['enrollment__candidate__first_name', 'lesson__title']
    readonly_fields = ['completed_at']