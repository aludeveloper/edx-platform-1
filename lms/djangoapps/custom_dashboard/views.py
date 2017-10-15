import logging
from django.shortcuts import render, render_to_response
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from alux_skills_map.models import (
        ScoredAssignment,
        Assignment,
        ScoredLearningOutcome,
        LearningOutcome
    )
from opaque_keys.edx.keys import CourseKey
from courseware.courses import get_course_by_id
# Create your views here.
log = logging.getLogger(__name__)

@login_required
@ensure_csrf_cookie
def custom_dashboard(request):
    """
        Function to render customized dashboard to Students
    """
    print "Custom Dashboard called"
    submittedAssignments = None
    # TODO - COLORS
    colors = [ 'red', 'green', 'blue', 'purple',
               'red', 'green', 'blue', 'purple',
               'red', 'green', 'blue', 'purple',
               'red', 'green', 'blue', 'purple']

    submittedAssignments = submitted_assignments(request)
    # upcoming_assginments = upcoming_assginments(request)

    submittedCoursesList = {}
    submittedAssignmentListColors = {}

    temp_color_cnt = 0
    for assignmentsData in submittedAssignments:
        assignment = assignmentsData.assignment
        temp_course = get_course_by_id(
                        CourseKey.from_string(assignment.course_id),
                        depth=0
                      )
        submittedCoursesList[assignment.course_id] = getattr(temp_course,
                                                    'display_name_with_default',
                                                    'Course Name'
                                                    )
        submittedAssignmentListColors[assignment.course_id] = colors[int(temp_color_cnt)]
        temp_color_cnt = int(temp_color_cnt) + 1
        if temp_color_cnt > 14:
            temp_color_cnt = 0

    context = {
        'submitted_assignments': submittedAssignments,
        'submittedCoursesList' : submittedCoursesList,
        'submittedAssignmentListColors' : submittedAssignmentListColors,
        # 'upcoming_assginments' : upcoming_assginments,
    }
    # import pdb;pdb.set_trace();

    return render_to_response('custom_dashboard/custom_dashboard.html', context)


@login_required
def submitted_assignments(request):
    """
        Function to get Submitted assignments objects by students
    """
    print "Submitted Assignments"
    scoredassignments = None
    try:
        scoredassignments = ScoredAssignment.objects.all().filter(published=True)
    except:
        log.info(
            u"No assignmets has been scores has been submitted for student %s",
            request.user.username
        )
    # context = {
    #     'scoredassignments':scoredassignments
    # }
    return scoredassignments



@login_required
def upcoming_assginments(request):
    """
        Function to get Upcoming assignments by students
    """
    print "Upcoming Assignments"
    upcomingassginments = None
    return upcomingassginments