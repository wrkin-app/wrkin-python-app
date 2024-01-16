from rest_framework import serializers

class ChatSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    user_id = serializers.IntegerField()
    name = serializers.CharField()
    is_task = serializers.BooleanField()
    message = serializers.SerializerMethodField()
    task = serializers.SerializerMethodField()
    sent_time = serializers.CharField(source='created_at')
    is_reply = False
    reply = serializers.SerializerMethodField()

    def get_message(self,obj):
        if not obj['is_task']:
            return {
                    "text":obj["message"],
                    "is_media":False,
                    "media":{
                                "type":"image",
                                "url":"url_link"
                    }
            }
        else:
            return {}
    
    def get_task(self, obj):
        if obj['is_task']:
            return {
                "id":obj["task_id"],
                "title": obj["task__title"],
                "description": obj["task__description"],
                "from_user":obj["task__from_user_id"],
                "to_user":obj["task__to_user_id"],
                "start_date":obj["task__start_date"],
                "end_date":obj["task__end_date"],
                "priority":obj["task__priority"]
            }
        else:
            return {}
    
    def get_reply(self,obj):
        return {}