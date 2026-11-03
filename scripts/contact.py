"""Contact CMS validation and legacy widget configuration synchronization."""
import html
import json
import re
from urllib.parse import quote

DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
EMAIL = r'[^\s@<>]+@[^\s@<>]+\.[^\s@<>]+'


def validate(contact):
    for name in ['email', 'recipientEmail']:
        if not re.fullmatch(EMAIL, contact[name]):
            raise ValueError(f'Invalid contact {name}')
    for name, low, high in [('latitude', -90, 90), ('longitude', -180, 180), ('zoom', 1, 20)]:
        if not low <= contact[name] <= high:
            raise ValueError(f'Invalid contact {name}')
    if len(contact['hours']) != 7 or {h['day'] for h in contact['hours']} != set(DAYS):
        raise ValueError('Contact hours must contain each weekday exactly once')
    for hour in contact['hours']:
        for name in ['open', 'close']:
            if not re.fullmatch(r'([01]\d|2[0-3]):[0-5]\d', hour[name]):
                raise ValueError('Contact hours must use HH:MM')


def text_targets(contact):
    return {
        'CONTACT_SECTION_TITLE_REND': [contact['title']],
        'CONTACT_INTRO_HEADING_REND': [contact['infoTitle']],
        'CONTACT_INFO_ADDRESS_REND': [contact['mapAddress']],
        'CONTACT_HOURS_TITLE_REND': [contact['hoursTitle']],
        'CONTACT_FORM_TITLE_REND': [contact['formTitle']],
        'CONTACT_FORM_REVEAL_BUTTON_REND': [contact['formTitle']] * 2,
    }


def info_lines(contact):
    return [f"Company Name: {contact['company']}", f"Registered Address: {contact['address']}",
            f"Contact Number: {contact['phone']}", f"Email: {contact['email']}"]


def html_targets(contact):
    escape = html.escape
    lines = info_lines(contact)
    info = ''.join(f'<p style="margin:0">{escape(line).replace(chr(10), "<br>")}</p>' for line in lines[:-1])
    info += f'<p style="margin:0">Email: <a href="mailto:{escape(contact["email"], quote=True)}">{escape(contact["email"])}</a></p>'
    rows = []
    for day in DAYS:
        hour = next(h for h in contact['hours'] if h['day'] == day)
        label = 'Closed' if hour['closed'] else f"{hour['open']} – {hour['close']}"
        rows.append(f'<tr><th scope="row">{day}</th><td>{escape(label)}</td></tr>')
    return {'CONTACT_INTRO_DESC_REND': info,
            'CONTACT_HOURS_REND': '<table class="contact-hours"><tbody>' + ''.join(rows) + '</tbody></table>'}


def update_widgets(source, contact):
    """Replace only the props for contact widgets, retaining shared context and handlers."""
    def replace(match):
        el, encoded = match.group('el'), match.group('props')
        props = json.loads(json.loads(encoded))
        if el == 'bs-2':
            props['structuredHours'] = [{'hour': {
                'day': h['day'], 'dayOfWeek': (DAYS.index(h['day']) + 1) % 7,
                'openTime': h['open'], 'closeTime': h['close'],
                'closed': h['closed'], 'byAppointmentOnly': False
            }} for h in contact['hours']]
        elif el == 'bs-3':
            props['formTitle'] = contact['formTitle']
            props['infoTitle'] = contact['infoTitle']
            props['info'] = json.dumps({'blocks': [{
                'key': f'cms{i}', 'text': line, 'type': 'unstyled', 'depth': 0,
                'inlineStyleRanges': [], 'entityRanges': [], 'data': {}
            } for i, line in enumerate(info_lines(contact))], 'entityMap': {}})
        elif el == 'bs-4':
            props.update(lat=str(contact['latitude']), lon=str(contact['longitude']),
                         address=contact['mapAddress'], zoom=contact['zoom'])
        value = json.dumps(json.dumps(props, ensure_ascii=True), ensure_ascii=True)
        return match.group(0).replace(encoded, value)

    pattern = r'''elId:'(?P<el>bs-[234])'.*?props:JSON.parse\((?P<props>"(?:\\.|[^"\\])*")\)'''
    result, count = re.subn(pattern, replace, source)
    if count != 3:
        raise ValueError('Missing contact widget configuration')
    return result


def update_form(source, contact):
    action = 'https://formsubmit.co/' + quote(contact['recipientEmail'], safe='@.+-')
    # JSON string encoding preserves quotes and newlines safely in generated JS.
    for prefix, value in [('contactForm.action', action), ('subjectField.value', contact['subject'])]:
        pattern = re.escape(prefix) + r' = "(?:\\.|[^"\\])*";'
        source, count = re.subn(pattern, lambda _: f'{prefix} = {json.dumps(value)};', source)
        if count != 1:
            raise ValueError(f'Missing form setting: {prefix}')
    return source
