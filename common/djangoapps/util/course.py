"""
Utility methods related to course
"""
import logging
import urllib

from django.conf import settings

log = logging.getLogger(__name__)

COURSE_SHARING_UTM_PARAMETERS = {
    'facebook': {
        'utm_medium': 'social-post',
        'utm_campaign': 'social-sharing',
        'utm_source': 'facebook',
    },
    'twitter': {
        'utm_medium': 'social-post',
        'utm_campaign': 'social-sharing',
        'utm_source': 'twitter',
    },
}


def get_encoded_course_sharing_utm_params():
    """
    Returns encoded Course Sharing UTM Parameters.
    """
    return {
        utm_source: urllib.urlencode(utm_params)
        for utm_source, utm_params in COURSE_SHARING_UTM_PARAMETERS.iteritems()
    }


def get_link_for_about_page(course):
    """
    Arguments:
        course: This can be either a course overview object or a course descriptor.

    Returns the course sharing url, this can be one of course's social sharing url, marketing url, or
    lms course about url.
    """
    is_social_sharing_enabled = getattr(settings, 'SOCIAL_SHARING_SETTINGS', {}).get('CUSTOM_COURSE_URLS')
    if is_social_sharing_enabled and course.social_sharing_url:
        course_about_url = course.social_sharing_url
    elif settings.FEATURES.get('ENABLE_MKTG_SITE') and getattr(course, 'marketing_url', None):
        course_about_url = course.marketing_url
    else:
        course_about_url = u'{about_base_url}/courses/{course_key}/about'.format(
            about_base_url=settings.LMS_ROOT_URL,
            course_key=unicode(course.id),
        )

    return course_about_url

def getAllCourseChildren(course_key, customDashboard=False):
    # from opaque_keys.edx.keys import CourseKey
    # course_key = CourseKey.from_string(course_id)
    from courseware.courses import get_course_by_id
    course = get_course_by_id(course_key, depth=2)
    course_name = course.display_name
    sections = []
    subsections = []
    units = []
    blocks = []
    coursewareids = {}
    if customDashboard:
        import datetime
        from django.utils import timezone
        from dateutil import parser
        from student.models import StudentSubmissionTracker
        # import pdb;pdb.set_trace();

        # get today's date at UTC
        d_today = datetime.datetime.now(timezone.utc)
        # d_today = d_today.date();

        # get next 7 days due date
        d_future = d_today + datetime.timedelta(days=7)

        for section in course.get_children():
            # hidden from students
            if section.visible_to_staff_only:
                continue
            # check release date
            if d_today < section.start:
                continue

            temp_section = {}
            temp_section['display_name'] = section.display_name
            temp_section['url_name'] = section.url_name
            temp_section['type'] = 'section'
            temp_section['course_name'] = course_name
            sections.append({temp_section['url_name']:temp_section})
            coursewareids[temp_section['url_name']] = temp_section

            # import pdb;pdb.set_trace();
            for subsection in section.get_children():
                # hidden from students
                if subsection.visible_to_staff_only:
                    continue
                # check release date
                if subsection.start:
                    if d_today < subsection.start:
                        continue
                # check due date
                if subsection.due:
                    if d_today > subsection.due:
                        continue
                    # check 7 days due date
                    if not (d_today <= subsection.due <= d_future):
                        continue
                temp_subsection = {}
                temp_subsection['url_name'] = subsection.url_name
                temp_subsection['display_name'] = subsection.display_name
                temp_subsection['parent'] = temp_section['url_name']
                temp_subsection['type'] = 'subsection'
                temp_subsection['course_name'] = course_name
                subsections.append(temp_subsection)
                coursewareids[temp_subsection['url_name']] = temp_subsection

                # import pdb;pdb.set_trace();
                for unit in subsection.get_children():
                    # hidden from students
                    if unit.visible_to_staff_only:
                        continue

                    temp_unit = {}
                    temp_unit['display_name'] = unit.display_name
                    temp_unit['url_name'] = unit.url_name
                    temp_unit['parent'] = temp_subsection['url_name']
                    temp_unit['type'] = 'unit'
                    temp_unit['course_name'] = course_name
                    units.append(temp_unit)
                    coursewareids[temp_unit['url_name']] = temp_unit

                    # import pdb;pdb.set_trace();
                    for block in unit.get_children():
                        # if not edx_ega , ORA
                        if block.category not in ['edx_sga', 'openassessment']:
                            continue
                        # default
                        block_due = None
                        if block.category == 'edx_sga':
                            # import pdb;pdb.set_trace();
                            if block.xblock_kvs._fields.get('cohort_deadlines', None):
                                for tmp_item in block.xblock_kvs._fields.get('cohort_deadlines').itervalues():
                                    if tmp_item.get('date', ''):
                                        block_due = parser.parse(tmp_item.get('date'))
                                        block_due = block_due.replace(tzinfo=timezone.utc)
                        if block.category == 'openassessment':
                            if block.submission_due:
                                block_due = parser.parse(block.submission_due)
                                block_due = block_due.replace(tzinfo=timezone.utc)

                        if not block_due and not subsection.due:
                            continue
                        if not block_due:
                            block_due = subsection.due

                        if not (d_today <= block_due <= d_future):
                            continue

                        # check assignment is submitted or not
                        submission_status = False
                        try:
                            studentsubmissiontracker = StudentSubmissionTracker.objects.get(
                                                        course_id="{}".format(course_key),
                                                        block_id=block.url_name
                                                        )
                            submission_status = studentsubmissiontracker.submission_status
                        except:
                            pass
                        temp_block = {}
                        temp_block['display_name'] = block.display_name
                        temp_block['url_name'] = block.url_name
                        temp_block['parent'] = temp_unit['url_name']
                        temp_block['type'] = 'block'
                        temp_block['submission_status'] = submission_status
                        temp_block['course_name'] = course_name
                        temp_block['course_id'] = "{}".format(course_key)
                        temp_block['due'] = block_due
                        temp_block['block_location'] = block.location
                        blocks.append(temp_block)
                        coursewareids[temp_block['url_name']] = temp_block
        if customDashboard:
            return blocks
    return coursewareids
    """ 
    # for future development
    for section in course.get_children():
        temp_section = {}
        if customDashboard:
            if section.visible_to_staff_only:
                continue
        temp_section['display_name'] = section.display_name
        temp_section['url_name'] = section.url_name
        temp_section['type'] = 'section'
        temp_section['course_name'] = course_name
        sections.append({temp_section['url_name']:temp_section})
        coursewareids[temp_section['url_name']] = temp_section
        import pdb;pdb.set_trace();
        for subsection in section.get_children():
            temp_subsection = {}
            temp_subsection['url_name'] = subsection.url_name
            temp_subsection['display_name'] = subsection.display_name
            temp_subsection['parent'] = temp_section['url_name']
            temp_subsection['type'] = 'subsection'
            temp_subsection['course_name'] = course_name
            subsections.append(temp_subsection)
            coursewareids[temp_subsection['url_name']] = temp_subsection
            import pdb;pdb.set_trace();
            for unit in subsection.get_children():
                temp_unit = {}
                temp_unit['display_name'] = unit.display_name
                temp_unit['url_name'] = unit.url_name
                temp_unit['due'] = unit.due
                temp_unit['parent'] = temp_subsection['url_name']
                temp_unit['type'] = 'unit'
                temp_unit['course_name'] = course_name
                units.append(temp_unit)
                coursewareids[temp_unit['url_name']] = temp_unit
                import pdb;pdb.set_trace();
                for block in unit.get_children():
                    temp_block = {}
                    temp_block['display_name'] = block.display_name
                    temp_block['url_name'] = block.url_name
                    temp_block['parent'] = temp_unit['url_name']
                    temp_block['type'] = 'block'
                    temp_block['course_name'] = course_name
                    blocks.append(temp_block)
                    coursewareids[temp_block['url_name']] = temp_block
    return coursewareids
    """