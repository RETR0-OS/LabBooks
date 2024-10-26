from django.urls import path
from LabBooks.course_manager import views
from . import views

app_name = "block_manager"

urlpatterns = [
    path('course/student/<int:course_id>/notebook/<int:notebook_id>', views.load_student_notebook, name="load_student_notebook"),
    path('course/student/<int:course_id>/notebook/<int:notebook_id>/evaluate/mcq/<int:block_id>', views.grade_mcq_question, name="grade_mcq_question"),
    path('course/student/<int:course_id>/notebook/<int:notebook_id>/evaluate/code/<int:block_id>', views.code_grader, name="code_grader"),
    path('course/teacher/<int:course_id>/notebook/<int:notebook_id>', views.load_teacher_notebook, name="load_teacher_notebook"),
    path('course/teacher/<int:course_id>/notebook/<int:notebook_id>/update', views.update_teacher_notebooks, name="update_teacher_notebook"),
    path('course/list/<int:course_id>', views.list_accessible_notebooks, name="list_accessible_notebooks"),
    path('course/teacher/<int:course_id>/notebook/create', views.create_notebook, name="create_notebook"),
    path('course/teacher/<int:course_id>/notebook/<int:notebook_id>/delete', views.delete_notebook, name="delete_notebook"),
    path('course/teacher/<int:course_id>/notebook/<int:notebook_id>/update', views.update_teacher_notebooks, name="update_notebook"),
    path('course/teacher/<int:course_id>/notebook/<int:notebook_id>/publish', views.publish_notebook, name="publish_notebook"),

]