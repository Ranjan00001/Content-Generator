import pprint
from services.presentation_service import PresentationService
# from ..services.presentation_service import PresentationService

def test_create_presentation(content):
    print("Testing create_presentation...")
    presentation = test_service.create_presentation(content)
    assert presentation is not None
    # Save presentation
    test_service.save_presentation(presentation, 'topic', 13, 'theme', ['layouts'])
    print("create_presentation passed!")

def test_fetch_content_from_gemini():
    print("Testing fetch_content_from_gemini...")
    content = test_service.fetch_content_from_gemini("How is the discovery of 5th world affecting humans?", 13, ["title", "bullet_points", "content_with_image", "title", "bullet_points", "two_column", "content_with_image", "title", "bullet_points", "two_column", "content_with_image", "title", "bullet_points"])
    pprint.pprint(content)
    # assert len(content) == 3
    # print("fetch_content_from_gemini passed!")
    return content

if __name__ == "__main__":
    # test_create_presentation()
    test_service = PresentationService()
    # a = test_fetch_content_from_gemini()
    a = [{'content': '',
    'image_path': '',
    'layout': 'title',
    'left_points': [],
    'points': [],
    'right_points': [],
    'subtitle': '',
    'title': 'The Hypothetical 5th World: Its Impact on Humanity'},
    {'content': '',
    'image_path': '',
    'layout': 'bullet_points',
    'left_points': [],
    'points': ['A 5th world typically refers to a hypothetical advanced '
                'extraterrestrial civilization.',
                'Its discovery could be through direct contact, detection of '
                'signals, or observation.',
                'The level of technological advancement of this civilization is '
                'highly speculative.'],
    'right_points': [],
    'subtitle': 'Understanding the hypothetical context',
    'title': "Defining the '5th World'"},
    {'content': 'The discovery could range from peaceful exchange to conflict, '
                'depending on the nature of the 5th world and our own '
                'preparedness.',
    'image_path': 'first_contact.jpg',
    'layout': 'content_with_image',
    'left_points': [],
    'points': [],
    'right_points': [],
    'subtitle': 'Potential outcomes of discovery',
    'title': 'First Contact Scenarios'},
    {'content': '',
    'image_path': '',
    'layout': 'title',
    'left_points': [],
    'points': [],
    'right_points': [],
    'subtitle': 'Potential benefits and challenges',
    'title': 'Technological Advancements'},
    {'content': '',
    'image_path': '',
    'layout': 'bullet_points',
    'left_points': [],
    'points': ['Access to new energy sources (e.g., fusion power).',
                'Advanced medicine and disease eradication.',
                'Potential for faster-than-light travel and exploration.'],
    'right_points': [],
    'subtitle': 'Gaining access to advanced technologies',
    'title': 'Technological Transfer'},
    {'content': '',
    'image_path': '',
    'layout': 'two_column',
    'left_points': ['Economic growth',
                    'Scientific breakthroughs',
                    'Improved quality of life'],
    'points': [],
    'right_points': ['Technological dependence',
                    'Resource depletion',
                    'Potential for conflict'],
    'subtitle': 'Weighing the potential consequences',
    'title': 'Positive vs. Negative Impacts'},
    {'content': 'The discovery could introduce unforeseen risks, such as hostile '
                'intentions, technological superiority, or the spread of unknown '
                'diseases.',
    'image_path': 'existential_risk.jpg',
    'layout': 'content_with_image',
    'left_points': [],
    'points': [],
    'right_points': [],
    'subtitle': 'Potential threats to human civilization',
    'title': 'Existential Risks'},
    {'content': '',
    'image_path': '',
    'layout': 'title',
    'left_points': [],
    'points': [],
    'right_points': [],
    'subtitle': 'Redefining our place in the universe',
    'title': 'Cultural and Philosophical Shifts'},
    {'content': '',
    'image_path': '',
    'layout': 'bullet_points',
    'left_points': [],
    'points': ['Re-evaluation of our place in the cosmos.',
                'New perspectives on human evolution and origins.',
                'Potential challenges to existing religious and philosophical '
                'systems.'],
    'right_points': [],
    'subtitle': 'Impact on religious and philosophical beliefs',
    'title': 'Changing Worldviews'},
    {'content': '',
    'image_path': '',
    'layout': 'two_column',
    'left_points': ['Unified global response',
                    'International collaboration on research'],
    'points': [],
    'right_points': ['Nationalistic competition', 'Potential for arms race'],
    'subtitle': 'Human response to the discovery',
    'title': 'Global Cooperation vs. Conflict'},
    {'content': 'Developing strategies for communication and interaction is '
                'crucial to mitigate risks and maximize potential benefits.',
    'image_path': 'preparing_for_contact.jpg',
    'layout': 'content_with_image',
    'left_points': [],
    'points': [],
    'right_points': [],
    'subtitle': 'The importance of proactive measures',
    'title': 'Preparing for Contact'},
    {'content': '',
    'image_path': '',
    'layout': 'title',
    'left_points': [],
    'points': [],
    'right_points': [],
    'subtitle': 'Navigating the moral implications',
    'title': 'Ethical Considerations'},
    {'content': '',
    'image_path': '',
    'layout': 'bullet_points',
    'left_points': [],
    'points': ['The discovery of a 5th world holds immense potential, but also '
                'significant risks.',
                'Careful consideration of ethical and practical implications is '
                'paramount.',
                'Our response will shape the future of humanity and our '
                'relationship with the cosmos.'],
    'right_points': [],
    'subtitle': 'The profound implications of discovery',
    'title': 'Conclusion: An Uncertain Future'}]
    test_create_presentation(a)

# Command to run this >>>  python -m test.presentation_service_test