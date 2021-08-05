from django.shortcuts import render
from rest_framework.response import Response
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from account.serializers import RegisterSerializer
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes,authentication_classes
import io
from django.contrib.auth import login
from account.models import User,PhoneOTP,Shopkeeper,Customer,Items,OrderItem,Order,Shopkeeper_Order_History,Customer_Order_History
from account.serializers import CreateUserSerializer,LoginUserSerializer,ShopkeeperSerializer,CustomerSerializer,ItemSerializer,soh_serializer,coh_serializer
from django.core.mail import send_mail
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from django.shortcuts import get_object_or_404
##from blissedmaths.utils import phone_validator, password_generator, otp_generator
import math,random
# Create your views here.
@csrf_exempt
@api_view(["POST"])
def register(request):

    serializer=RegisterSerializer(data=request.data)

    if serializer.is_valid():


        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors)
def otp_generator() : 
   
    digits = "0123456789"
    OTP = "" 
    for i in range(4) : 
        OTP += digits[math.floor(random.random() * 10)] 
  
    return OTP 

def send_otp(phone):
    """
    This is an helper function to send otp to session stored phones or 
    passed phone number as argument.
    """

    if phone:
        
        key = otp_generator()
        phone = str(phone)
        otp_key = str(key)

        #link = f'https://2factor.in/API/R1/?module=TRANS_SMS&apikey=fc9e5177-b3e7-11e8-a895-0200cd936042&to={phone}&from=wisfrg&templatename=wisfrags&var1={otp_key}'
   
        #result = requests.get(link, verify=False)

        return otp_key
    else:
        return False

def sendotp_email(email):

    if email:
            key = otp_generator()
            email = str(email)
            otp_key = str(key)
            # subject = 'Please Confirm Your Account'
            # message = 'Your 4 Digit Verification Pin: {}'.format(otp_key)
            # email_from = '*****'
            # recipient_list = [str(emaill), ]
            # send_mail(subject, message, email_from, recipient_list)
            return otp_key
    else:
        return False


@api_view(["POST"])
@csrf_exempt
def ValidatePhoneSendOTP(request):
    '''
    This class view takes phone number and if it doesn't exists already then it sends otp for
    first coming phone numbers'''

    
    phone_number = request.data.get('phone')
    print(phone_number)
    val=1
    if phone_number:
        username=phone_number
        val=0
    else:
        username=request.data.get('email')
    if username:
            username = str(username)
            user = User.objects.filter(username = username)
            if user.exists():
                return Response({'status': False, 'detail': 'User already exists'})
                 # logic to send the otp and store the phone number and that otp in table. 
            else:
                if val==0:
                    otp = send_otp(username)
                else:
                    otp=sendotp_email(username)
                print(username, otp)
                if otp:
                    otp = str(otp)
                    count = 0
                    old = PhoneOTP.objects.filter(username = username)
                    if old.exists():
                        count = old.first().count
                        old.first().count = count + 1
                        old.first().save()
                    
                    else:
                        count = count + 1
               
                        PhoneOTP.objects.create(
                             username =  username, 
                             otp =   otp,
                             count = count
        
                             )
                    if count > 7:
                        return Response({
                            'status' : False, 
                             'detail' : 'Maximum otp limits reached. Kindly support our customer care or try with different number'
                        })
                    
                    
                else:
                    return Response({
                                'status': 'False', 'detail' : "OTP sending error. Please try after some time."
                            })

                return Response({
                    'status': True, 'detail': 'Otp has been sent successfully.'
                })
    else:
            return Response({
                'status': 'False', 'detail' : "I haven't received any phone number/e-mail. Please do a POST request."
            })

@api_view(["POST"])
@csrf_exempt
def ValidateOTP(request):
    '''
    If you have received otp, post a request with phone and that otp and you will be redirected to set the password
    
    '''

    
    phone = request.data.get('phone', False)
    if phone:
        username=phone
    else:
        username=request.data.get('email',False)
    otp_sent   = request.data.get('otp_sent', False)
    print(username,otp_sent)
    if username and otp_sent:
            old = PhoneOTP.objects.filter(username = username)
            if old.exists():
                old = old.first()
                otp = old.otp
                if str(otp) == str(otp_sent):
                    old.logged = True
                    old.save()

                    return Response({
                        'status' : True, 
                        'detail' : 'OTP matched, kindly proceed to save password'
                    })
                else:
                    return Response({
                        'status' : False, 
                        'detail' : 'OTP incorrect, please try again'
                    })
            else:
                return Response({
                    'status' : False,
                    'detail' : 'Phone/E-mail not recognised. Kindly request a new otp with this number/e-mail'
                })


    else:
            return Response({
                'status' : 'False',
                'detail' : 'Either phone/emaail or otp was not recieved in Post request'
            })

@api_view(["POST"])
@csrf_exempt
def Register(request):

    '''Takes phone and a password and creates a new user only if otp was verified and phone is new'''

    
    serializer1=RegisterSerializer(data=request.data)
    if serializer1.is_valid():
            phone=request.data.get('phone',False)
            val=0
            if phone:
                username=phone
            else:
                val=1
                username=request.data.get('email',False)
            password=request.data.get('password',False)
           
            print(username)
            print(password)
                
            if username and password:
                    username = str(username)
                    user = User.objects.filter(username = username)
                    if user.exists():
                        return Response({'status': False, 'detail': 'Phone Number/E-mail  already have account associated. Kindly try forgot password'})
                    else:
                        old = PhoneOTP.objects.filter(username = username)
                        print(old)
                        if old.exists():
                            old = old.first()
                            if old.logged:
                                Temp_data = {'username': username, 'password': password }

                                serializer = CreateUserSerializer(data=Temp_data)
                                serializer.is_valid(raise_exception=True)
                                user = serializer.save()
                                user.save()
                                ###Create Customer or Shopkeeper
                                if val==0:
                                    log_value='phone'
                                else:
                                    log_value='email'
                                name=request.data.get('Name',None)
                                email=request.data.get('email',None)
                                phone=request.data.get('phone',None)
                                ##print(request.data.get('shopkeeper'))
                                serializer1.is_valid()
                                if serializer1.validated_data['shopkeeper']:
                                    print(type(serializer1.validated_data['shopkeeper']))
                                    Shopkeeper.objects.create(user1=user,loggedin_with=log_value,Owner_name=name,email=email,phone=phone)
                                else:
                                    ## Create Customer
                                    Customer.objects.create(user1=user,loggedin_with=log_value,Name=name,email=email,phone=phone)

                                old.delete()
                                return Response({
                                    'status' : True, 
                                    'detail' : 'Congrts, user has been created successfully.'
                                })

                            else:
                                return Response({
                                    'status': False,
                                    'detail': 'Your otp was not verified earlier. Please go back and verify otp'

                                })
                        else:
                            return Response({
                            'status' : False,
                            'detail' : 'Phone number/E-mail not recognised. Kindly request a new otp with this number/e-mail'
                        })
                            




            else:
                    return Response({
                        'status' : 'False',
                        'detail' : 'Either phone/e-mail or password was not recieved in Post request'
                    })
    else:
        return Response(serializer1.errors)


@api_view(["POST"])
# @permission_classes([permissions.AllowAny,])
@csrf_exempt
def Login(request):
        print(request.user)
        serializer = LoginUserSerializer(data=request.data)
        if serializer.is_valid():
        
            user = serializer.validated_data['user']
                
            login(request, user)
            print(request.user)
            return Response({
                    'status' : 'True',
                                'detail' : 'user logged in successfully'

                })
        else:
                return Response({
                    'status' : 'False',
                                'detail' : 'Incorrect credentials'

                })
@api_view(["POST","PUT"])
# @permission_classes([permissions.AllowAny,])
@csrf_exempt
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def update_profile(request):

    if request.method=='PUT':
        username=request.user.username
        
        obj=Customer.objects.filter(user1__username=username)
        print(username)
        print(obj)
        if len(obj)==1:
            obj1=Customer.objects.get(user1__username=username)
            serializer=CustomerSerializer(obj1,data=request.data,partial=True,context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response({"Profile updated successfuly"})
        
            return Response(serializer.errors)
        else:
            obj1=Shopkeeper.objects.get(user1__username=username)
            serializer=ShopkeeperSerializer(obj1,data=request.data,partial=True,context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response({"Profile updated successfuly"})
        
           
        
        return Response(serializer.errors)


@api_view(['GET'])
def get_restaurants(request,pk=False,name=False):
    print(pk)
    if not pk:
        if name:
            restaurants=Shopkeeper.objects.filter(Restaurant_name=name)
        else:   
            restaurants=Shopkeeper.objects.all()
        
    else:
        restaurants=Shopkeeper.objects.filter(Category=pk)
    serializer=ShopkeeperSerializer(restaurants,many=True)
    return Response(serializer.data)


@api_view(["POST","PUT"])
# @permission_classes([permissions.AllowAny,])
@csrf_exempt
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def add_items(request):
 
    if request.method=='POST':
        serializer=ItemSerializer(data=request.data,context={'request': request})
        if serializer.is_valid():
            user1=Shopkeeper.objects.get(user1=request.user)
            Items.objects.create(user1=user1,Name=serializer.validated_data['Name'],
                Description=serializer.validated_data['Description'],Price=serializer.validated_data['Price'],)
            return Response({"Item added successfully"})
        return Response(serializer.errors)

@api_view(['GET'])
##get items by restautant , by category, by name
def get_items(request,pk=False,name=False,category=False):
    ## get items by restaurant
        print("hi")
        if pk and not name and not category:
            restaurant=Shopkeeper.objects.get(id=pk)

            li=Items.objects.filter(user1=restaurant)
        
        print(li)
        if pk and name and not category:
            restaurant=Shopkeeper.objects.get(id=pk)
            print(restaurant)
            li=Items.objects.filter(Name=name).filter(user1=restaurant)
        if pk and not name and category:
            restaurant=Shopkeeper.objects.get(id=pk)
            print(restaurant,category)
            li=Items.objects.filter(Category=category).filter(user1=restaurant)
            print(li)
        serializer=ItemSerializer(li,many=True)
        return Response(serializer.data)


@api_view(["POST","PUT"])
# @permission_classes([permissions.AllowAny,])
@csrf_exempt
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def add_remove_favourite_restaurant(request,pk):
    restaurant=Shopkeeper.objects.get(id=pk)
    customer=Customer.objects.get(user1=request.user)
    if customer in restaurant.favourite_restaurants.all():
        restaurant.favourite_restaurants.remove(customer)
    else:
        restaurant.favourite_restaurants.add(customer)
    return Response({"Updated Successfully"})
    
    

@api_view(["POST","PUT"])
# @permission_classes([permissions.AllowAny,])
@csrf_exempt
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def add_remove_favourite_item(request,pk):
    item=Items.objects.get(id=pk)
    customer=Customer.objects.get(user1=request.user)
    print(item,customer)
    if customer in item.favourite_items.all():
        item.favourite_items.remove(customer)
    else:
        item.favourite_items.add(customer)
    return Response({"Updated Successfully"})


@api_view(['GET'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def user_favourite_restaurants(request):
    customer=Customer.objects.get(user1=request.user)
    user_favourites = Shopkeeper.objects.filter(favourite_restaurants=customer)
    serializer=ShopkeeperSerializer(user_favourites,many=True)
    return Response(serializer.data)


    
@api_view(['GET'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def user_favourite_items(request):
    customer=Customer.objects.get(user1=request.user)
    user_favourites=Items.objects.filter(favourite_items=customer)
    serializer=ItemSerializer(user_favourites,many=True)
    return Response(serializer.data)


@api_view(['POST'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def add_to_cart(request, pk):
    item = get_object_or_404(Items, pk=pk)
    customer=Customer.objects.get(user1=request.user)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=customer
        ##ordered=False
    )
    order_qs = Order.objects.filter(user=customer)

    if order_qs.exists():
        order = order_qs[0]

        if order.items.filter(item__pk=item.pk).exists():
            order_item.quantity += 1
            order_item.save()
            return Response({"message": "Added quantity Item", },
                            ##status=status.HTTP_200_OK
                            )
        else:
            order.items.add(order_item)
            return Response({"message": " Item added to your cart", },
                           ## status=status.HTTP_200_OK,
                            )
    else:
        ##ordered_date = datetime.timezone.now()
        order = Order.objects.create(user=customer)
        order.items.add(order_item)
        return Response({"message": "Item added to your cart", },
                       ## status=status.HTTP_200_OK,
                        )
@api_view(['POST'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def request_order(request,pk):
    shopkeeper=Shopkeeper.objects.get(id=pk)
    customer=Customer.objects.get(user1=request.user)
    order=Order.objects.get(user=customer)
    print(shopkeeper,customer,order.user)
    Shopkeeper_Order_History.objects.create(user=shopkeeper,order=order)
    Customer_Order_History.objects.create(user=customer,order=order)
    return Response({"Order requested!!"})

@api_view(['POST'])
def shopkeeper_accept(request,pk):
    obj=Shopkeeper_Order_History.objects.get(id=pk)
    print(obj)
    obj.status=True
    obj.save()
    order=obj.order
    obj1=Customer_Order_History.objects.get(order=order)
    obj1.status=True
    obj1.save()
   
    return Response({"Order accepted!!"})



@api_view(['POST'])
def shopkeeper_reject(request,pk):
    obj=Shopkeeper_Order_History.objects.get(id=pk)
    
    order=obj.order
    obj.delete()
    obj1=Customer_Order_History.objects.get(order=order)
    obj1.delete()
    return Response({"Order cancelled!!"})



@api_view(['POST'])
def customer_reject__(request):
    obj=Customer_Order_History.objects.get(id=pk)
    
    order=obj.order
    obj.delete()
    obj1=Shopkeeper_Order_History.objects.get(order=order)
    obj1.delete()
    return Response({"Order cancelled!!"})


# @api_view(['GET'])
# def shopkeeper_order_history(request):
#     shopkeeper=Shopkeeper.objects.get(user1=request.user)
#     obj=Shopkeeper_Order_History.objects.get(user=shopkeeper)
#     serializer=soh_serializer(obj,many=True)
#     return Response(serializer.data)

# @api_view(['GET'])
# def customer_order_history(request):
#     customer=Customer.objects.get(user1=request.user)
#     print(customer)
#     obj=Customer_Order_History.objects.get(user=customer)
#     serializer=coh_serializer(obj,many=True)
#     return Response(serializer.data)

