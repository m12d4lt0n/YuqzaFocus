from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import cohere
import json
from gtts import gTTS
import random
import string
import base64
from rest_framework.exceptions import ParseError


keyToken = "YYZk4mNTkJNR0EUpuqkVRltqVucpnOwqEG1gBYZk"

def TextToSpeech(text):
    tts = gTTS(text=text, lang='ar')
    random_text = ''.join(random.choices(string.ascii_letters, k=20))
    filename = base64.b64encode(random_text.encode('utf-8')).decode('utf-8')
    tts.save(f"../voices/{filename}.mp3")

    return filename

    


def cohereAIgenerator(rules, data, message):
    if data.get('severityLevel') in ['mild', 'moderate', 'severe']:
        co = cohere.ClientV2(keyToken)
        severity_level = data.get('severityLevel', 'mild')
        arabic_severity = {'mild': 'خفيف', 'moderate': 'متوسط', 'severe': 'شديد'}.get(severity_level, 'خفيف')
        try:
            response = co.chat(
                model="command-r-plus-08-2024",
                messages=[
                    {"role": "system", "content": rules},
                    {"role": "user", "content": f"{message}, المستوى: {arabic_severity}"}
                ],
                temperature=0.65,
            )
            raw_text = response.message.content[0].text
            try:
                json_data = json.loads(raw_text)
                return {"isvalid": True, "data": json_data}
            except json.JSONDecodeError:
                return {"isvalid": False, "data": {"error": "Invalid JSON format", "message": raw_text}}
        except Exception as e:
            return {"isvalid": False, "data": {"error": "Cohere API error", "message": str(e)}}
    return {"isvalid": False, "data": {"error": "Invalid severity level"}}


class adhd(APIView):  # Updated to remove the misplaced block
    def post(self, request):
        try:
            severity_level = request.data.get('severityLevel')
        except ParseError:
            return Response(
                {"error": "Invalid JSON format. Ensure property names are enclosed in double quotes."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if severity_level not in ['mild', 'moderate', 'severe']:
            return Response(
                {"error": "Invalid or missing severity level. Accepted values are: mild, moderate, severe."},
                status=status.HTTP_400_BAD_REQUEST
            )

        rules = """
        - Generate ADHD-focused interactive story in Arabic
        - Strict structure: 20 sequential stages without loops
        - User must provide "severityLevel" (mild/moderate/severe)
        - Tailor story content and impacts to specified severity:
        * Mild: Subtle challenges, smaller impacts (-0.5 to +0.5)
        * Moderate: Clear symptoms, medium impacts (-0.7 to +0.7)
        * Severe: Intense struggles, full range (-1 to +1)
        - Required JSON structure:
        {
        "storyTitle": "string",
        "stages": [
            {
            "stage": number (1-20),
            "text": "string",
            "choices": [
                {
                "text": "string",
                "next_stage": number/null,
                "adhd_impact": number (range varies by severity)
                }
            ]
            }
        ]
        }
        - The difficulty of the story or the length of each text, even the minimum, depends on the level of the case.
        - You are creating a story for a sick child, so do not respond or talk outside the story line at all. Make sure that the last line is next_stage null.
        - Final stage must end with next_stage: null
        - Validate JSON syntax rigorously
        - No markdown formatting
        - make sure that you did all previous rules
        """
        r = cohereAIgenerator(rules, request.data, "أنشئ قصة تفاعلية لمرحلة متقدمة من فرط الحركة")

        if r['isvalid']:
            return Response(r['data'], status=status.HTTP_201_CREATED)
        return Response(r['data'], status=status.HTTP_400_BAD_REQUEST)


class dyslexia(APIView):  # Updated to include the moved block
    def post(self, request):
        try:
            severity_level = request.data.get('severityLevel')
        except ParseError:
            return Response(
                {"error": "Invalid JSON format. Ensure property names are enclosed in double quotes."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if severity_level not in ['mild', 'moderate', 'severe']:
            return Response(
                {"error": "Invalid or missing severity level. Accepted values are: mild, moderate, severe."},
                status=status.HTTP_400_BAD_REQUEST
            )

        rules = """
        - Generate 10 dyslexia reading exercises in Arabic
        - Each exercise must:
        * Present a simple sentence with target letter missing
        * Provide 4 similar-looking letter options (e.g., ب ت ث)
        * Include one correct and three incorrect choices
        - Target similar letter groups:
        * ب ت ث
        * ج ح خ
        * د ذ
        * ر ز
        * س ش
        * ص ض
        * ط ظ
        * ع غ
        * ف ق
        - Required JSON structure:
        {
        "exercises": [
            {
            "exerciseNumber": number,
            "originalText": " النص الأصلي بالكامل ويكون طولة اقل شئ 3 كلمات حسب شدة الحالة",
            "questionText": "الكلمة مع الحرف المستهدف الناقص __ مثلا اذا النص الاصلي لكلمة القطط تكون القـ_ط ويكون الحرف الناقص الطاء وتأكد ان المحذوف حرف واحد فقط"
            "targetLetter": "الحرف المستهدف",
            "targetword" : "الكلمة المستهدفة"
            "options": [
                {, "text": "حرف", "isCorrect": True/False, "impact": -1 to +1},
                // 3 more options
            ],
            }
        ]
        }
            return Response(r['data'], status=status.HTTP_201_CREATED)
        - Make sure you delete only one character from the questionText only one and check it more one time to make sure you delete only one letter.
        - The text that is affected and increases in length or decreases to a minimum of 3 words is the originalText.
        - be sure that you work only with the target similar letter groups
        - Ensure:
        * No duplicate letters in options
        * Correct letter matches target
        * Impact values reflect difficulty
        - Output plain JSON only
        - Validate JSON syntax rigorously
        """
        r = cohereAIgenerator(rules, request.data, "أنشئ تمارين ديسليكسيا مع قياس التأثير")
        
        if r['isvalid']:
        #     if 'originalText' in r['data']:
        #         r['audio'] = TextToSpeech(r['originalText'])
           return Response(r['data'], status=status.HTTP_201_CREATED)
        #     else:
        #         return Response(
        #             {"error": f"The response from the AI generator is missing the 'originalText' field. {type(r)}"},
        #             status=status.HTTP_500_INTERNAL_SERVER_ERROR
        #         )
        return Response(r['data'], status=status.HTTP_400_BAD_REQUEST)
