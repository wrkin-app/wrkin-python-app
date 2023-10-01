from django.db.models import F,Value,Case,CharField,When
ROLES_CHOICES = Case(
                                                            When(role=1, then=Value('super_admin')),
                                                            When(role=2, then=Value('sales')),
                                                            default=Value('Unknown'),
                                                            output_field=CharField()
                                                          )
import re
def loginValidator(data):
    try:
        email = data['email']
    except:
        res = {
                'status':False,
                'message':'email is required'
              }
        return res
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email): 
        res = {
                'status':False,
                'message':'please provide a proper email'
              }
        return res
    try:
        email = data['password']
    except:
        res = {
                'status':False,
                'message':'password is required'
              }
        return res
    res = {'status':True}
    return res
