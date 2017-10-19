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
from django.http import HttpResponse
import json
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
    colors = [ '#CA0022', '#283070', '#1DAA3A', '#E9DF34',
               '#328FE1', '#A20089', '#EB6900', '#108850',
               '#2AC5C0', '#590095', '#753407', '#E7AB18',
               '#A037E7', '#30650C', '#DE52BC', '#8DC8E4',
               '#F68E69', '#137E7A', '#DC3C0C', '#E2F68F',
               '#890001', '#8CCC44', '#F99AB9', '#000000' ]

               

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
        submittedAssignmentListColors[assignment.course_id] = colors[int(temp_color_cnt % 24)]
        temp_color_cnt = int(temp_color_cnt) + 1

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
        scoredassignments = ScoredAssignment.objects.all().filter(published=True, user=request.user).order_by('-updated')
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


@login_required
def get_feedback(request):
    """
        Function returns specific student feedback details for an assignment
    """
    if request.method == "POST":
        assignment_id = request.POST.get('assignmentid', 0)
        student_id = request.user
        assignment_lo_rubric = []
        assignmentsData = {}
        try:
            assignment = Assignment.objects.all().filter(id=assignment_id)
            if assignment:
                scoredassignment = ScoredAssignment.objects.all().filter(assignment=assignment[0],
                                                                        user=student_id)
                temp_course = get_course_by_id(
                                CourseKey.from_string(assignment[0].course_id),
                                depth=0
                              )
                assignmentsData['course_name'] = getattr(temp_course,
                                                        'display_name_with_default',
                                                        'Course Name'
                                                    )
                assignmentsData['assignment_name'] = assignment[0].name[assignment[0].name.index('(')+1:assignment[0].name.index(')')]

                if scoredassignment:
                    assignmentsData['overall_feedback'] = scoredassignment[0].comments
                    assignmentsData['overall_score'] = scoredassignment[0].score

                    scoredlearningoutcomes = ScoredLearningOutcome.objects.all().filter(scored_assignment=scoredassignment[0])
                    for slc in scoredlearningoutcomes:
                        learning_outcome = slc.learning_outcome
                        learningoutcometable = {
                            'lc_level_zero_description' : '',
                            'lc_level_one_description': learning_outcome.level_one_description,
                            'lc_level_two_description' : learning_outcome.level_two_description,
                            'lc_level_three_description' : learning_outcome.level_three_description,
                            'lc_level_four_description' : learning_outcome.level_four_description,
                            'lc_level_five_description' : learning_outcome.level_five_description,
                            'lc_description': learning_outcome.description,
                            'slc_score' : int(slc.score),
                            'slc_comment' : slc.comments
                        }
                        assignment_lo_rubric.append(learningoutcometable)
                    content = json.dumps({'assignment_lo_rubric':assignment_lo_rubric,
                                          'assignmentsData':assignmentsData
                                        })
                    return HttpResponse(content, content_type="application/javascript",
                                    status=200)

        except:
            return HttpResponse(status=400)
        return HttpResponse(status=400)
        
    else:
        return HttpResponse(status=400)