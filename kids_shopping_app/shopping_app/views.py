from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.db import IntegrityError
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.http import HttpResponse
from .models import Buyer, Order, OrderItem, Item, Store, Seller, Review
from .forms import ProductForm, ReviewForm, RegistrationForm
from django.core.mail import send_mail
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import StoreSerializer, ItemSerializer, ReviewSerializer
import tweepy


def is_seller(user):
    '''Used to determine if user is a seller.'''
    return hasattr(user, 'seller')


def home(request):
    """Homepage with options to sort by store or price"""
    sort_by = request.GET.get('sort', '')

    if sort_by == 'store':
        all_items = Item.objects.all().order_by('store__name')
    elif sort_by == 'price':
        all_items = Item.objects.all().order_by('price')
    else:
        all_items = Item.objects.all()

    for item in all_items:
        item.all_reviews = item.reviews.all()

    return render(request, 'shopping_app/homepage.html', {
        'items': all_items,
        'sort_by': sort_by,
        'page_title': 'Welcome to the Marketplace'
    })


@csrf_exempt
def register_user(request):
    """Allows a user to register as a buyer or seller.
    Will send a tweet when a new store is created.
    Set error message since posting is unavailable
    without paid sub to X."""
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            email = form.cleaned_data['email']
            name = form.cleaned_data['name']
            user_type = form.cleaned_data['user_type']

            if User.objects.filter(username=username).exists():
                form.add_error('username',
                               'This username is already taken.')
                return render(request, "shopping_app/register.html",
                              {"form": form})

            try:
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    email=email
                )

                if user_type == 'buyer':
                    Buyer.objects.create(user=user, name=name, email=email)
                    login(request, user)
                    return redirect("home")
                else:
                    seller = Seller.objects.create(user=user, name=name)
                    store = Store.objects.create(
                        seller=seller,
                        name=f"{seller.name}'s Storefront"
                    )
                    try:
                        send_tweet(f"New store opened: {store.name}!")
                    except Exception as e:
                        print("Tweet Failed, need Paid Access.", e)
                    login(request, user)
                    return redirect("view_store", pk=store.pk)

            except IntegrityError:
                form.add_error(None, "An error occurred. Please try again.")
                return render(request, "shopping_app/register.html",
                              {"form": form})

        return render(request, "shopping_app/register.html", {"form": form})

    else:
        form = RegistrationForm()
        return render(request, "shopping_app/register.html", {"form": form})


def add_to_cart(request, item_id):
    """Add items to cart, creating one if none available.
    Keeps track of items with sessions."""
    item = Item.objects.get(id=item_id)
    cart = request.session.get('cart', [])
    item_found = False

    for cart_item in cart:
        if cart_item['item_id'] == item.id:
            cart_item['quantity'] += 1
            item_found = True
            break

    if not item_found:
        cart.append({
            'item_id': item.id,
            'quantity': 1,
            'name': item.name,
            'price': float(item.price),
        })

    request.session['cart'] = cart

    return redirect('view_cart')


def view_cart(request):
    """Allows the user to view items and quantities in their
    shopping cart."""

    cart_items = request.session.get('cart', [])
    total = sum(item['quantity'] * item['price'] for item in cart_items)
    buyer_name = request.user

    return render(request, "items/view_cart.html",
                  {"buyer_name": buyer_name,
                   "cart_items": cart_items, "total": total})


@user_passes_test(is_seller)
def add_item_to_store(request):
    """Generates store content using a form for user
    to enter item name, description, price, and quantity.
    Updated to post to X when new item is added.
    Posting unavailable without paid subscription."""

    seller = Seller.objects.get(user=request.user)
    store = Store.objects.get(seller=seller)

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.store = store
            item.save()
            try:
                send_tweet(f"{seller.name} just added: {item.name}!")
                return redirect("view_store", pk=store.pk)
            except Exception as e:
                print("Tweet failed without paid sub", e)
    else:
        form = ProductForm()

    return render(request, "shopping_app/item_form.html", {
        "form": form,
        "store": store
    })


@login_required
def item_update(request, pk):
    """View to update an existing item in store."""
    item = get_object_or_404(Item, pk=pk)

    if item.store.seller.user != request.user:
        print("Redirecting because the user is not the seller of the store")
        return redirect('home')

    store_pk = item.store.pk

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            item = form.save(commit=False)
            item.save()
            return redirect("view_store", pk=store_pk)
    else:
        form = ProductForm(instance=item)

    return render(request, 'shopping_app/item_update.html',
                  {'form': form, 'item': item})


@login_required
def item_delete(request, pk):
    """View to delete an existing item.
    :param request: HTTP request object.
    :param pk: Primary key of the item to be deleted.
    :return: Redirect to the item list after deletion."""
    item = get_object_or_404(Item, pk=pk)
    store_pk = item.store.pk
    item.delete()
    return redirect("view_store", pk=store_pk)


def view_item_detail(request, item_id):
    '''Takes the user to the item detail
    page where they can see all reviews.'''
    item = get_object_or_404(Item, id=item_id)
    reviews = item.reviews.all()

    return render(request, "shopping_app/item_detail.html", {
        "item": item,
        "reviews": reviews,
    })


@user_passes_test(is_seller)
def view_store(request, pk):
    """The seller's storefront where they can view their items"""
    seller = Seller.objects.get(user=request.user)
    store = get_object_or_404(Store, pk=pk, seller=seller)
    items = store.item_set.all()

    context = {
        "store": store,
        "items": items,
        "page_title": f"{store.seller.name}'s Store",
    }

    return render(request, "shopping_app/store.html", context)


@login_required
def checkout(request):
    """Takes user to checkout, must be a buyer
    if not a buyer, shows option to register as one"""
    if hasattr(request.user, 'seller') and request.user.seller:
        messages.error(request,
                       "Please register as a buyer to make purchases.")
        return redirect('home')

    try:
        buyer = Buyer.objects.get(user=request.user)
    except Buyer.DoesNotExist:
        return redirect('create_buyer_account')

    cart_items = request.session.get('cart', [])
    if not cart_items:
        messages.error(request, "There are no items in your cart.")
        return redirect("view_cart")

    total = sum(item['quantity'] * item['price'] for item in cart_items)

    order = Order.objects.create(buyer=buyer, total_price=total, status='paid')

    for cart_item in cart_items:
        item = Item.objects.get(id=cart_item['item_id'])
        OrderItem.objects.create(
            order=order,
            item=item,
            quantity=cart_item['quantity'],
            price=cart_item['price']
        )

    item_lines = "\n".join(
        f"{item['name']} - ${item['price']} x {item['quantity']}" for item in cart_items
    )
    invoice_text = f"Invoice for {request.user.email}\n\nItems:\n{item_lines}\n\nTotal: ${total}"

    send_mail(
        subject="Your Kinder Shop Invoice",
        message=invoice_text,
        from_email="noreply@kindershop.com",
        recipient_list=[request.user.email],
        fail_silently=True,
    )

    request.session['cart'] = []

    return render(request, "shopping_app/invoice.html", {
        "cart_items": cart_items,
        "total": total,
    })


def item_list(request):
    '''Lists items by store owner.'''
    sort_by = request.GET.get('sort')

    if sort_by == 'store':
        items = Item.objects.select_related('store').order_by('store__name',
                                                              'name')
    else:
        items = Item.objects.all()

    stores = Store.objects.all()

    return render(request, 'shopping_app/item_list.html', {
        'items': items,
        'stores': stores,
        'sort_by': sort_by})


@login_required
def leave_review(request, item_id):
    '''Allows users to leave reviews as verified
    if they've purchased the item, or
    unverified if not.'''
    item = get_object_or_404(Item, id=item_id)

    try:
        buyer = request.user.buyer
    except Buyer.DoesNotExist:
        messages.error(request,
                       "You need to be a registered buyer to leave a review.")
        return redirect('item_detail', item_id=item.id)

    has_purchased = OrderItem.objects.filter(
        order__buyer=buyer,
        item=item
    ).exists()

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            Review.objects.create(
                item=item,
                buyer=buyer,
                rating=form.cleaned_data['rating'],
                comment=form.cleaned_data['comment'],
                verified=has_purchased
            )
            messages.success(request, "Your review has been submitted.")
            return redirect('item_detail', item_id=item.id)

        else:
            print("Form errors:", form.errors)
    else:
        form = ReviewForm()

    return render(request, 'shopping_app/leave_review.html', {
        'item': item,
        'form': form
    })


def create_buyer_account(request):
    """Creates new buyer account and logs them in"""
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
                email=form.cleaned_data['email']
            )

            Buyer.objects.create(user=user, name=form.cleaned_data['name'])

            login(request, user)

            return redirect('home')
    else:
        form = RegistrationForm()

    return render(request, 'shopping_app/create_buyer_account.html',
                  {'form': form})


@api_view(['POST'])
def api_login(request):
    """API login that accepts a username and password,
    using POST. If either field is blank, returns a
    400 error. If successful, 200 OK. If there is a
    mismatch, 401 is returned."""
    username = request.data.get('username')
    password = request.data.get('password')

    if username is None or password is None:
        return Response({'error': 'Please provide a username and password.'},
                        status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(username=username, password=password)

    if user:
        login(request, user)
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token

        return Response({'message': 'Login successful',
                         'access_token': str(access_token),
                         }, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Invalid.'},
                        status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_store(request):
    if not hasattr(request.user, 'seller'):
        return Response({'detail': 'You must be a seller to create a store.'},
                        status=status.HTTP_403_FORBIDDEN)

    if Store.objects.filter(seller=request.user.seller).exists():
        return Response({'detail': 'You already have a store.'},
                        status=status.HTTP_400_BAD_REQUEST)

    data = request.data
    data['seller'] = request.user.id

    serializer = StoreSerializer(data=data)

    if serializer.is_valid():
        serializer.save(seller=request.user.seller)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_add_item(request):
    serializer = ItemSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_get_reviews(request, store_id=None, item_id=None):
    if store_id:
        items = Item.objects.filter(store_id=store_id)
        reviews = Review.objects.filter(item__in=items)
    elif item_id:
        reviews = Review.objects.filter(item_id=item_id)
    else:
        return Response({"detail": "Either item or store must be provided."},
                        status=status.HTTP_400_BAD_REQUEST)

    serializer = ReviewSerializer(reviews, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


class StoreListBySeller(APIView):
    permission_classes = [IsAuthenticated]

    def get_store(self, request, seller_id, format=None):
        try:
            stores = Store.objects.filter(seller_id=seller_id)
            serializer = StoreSerializer(stores, many=True)
            return Response(serializer.data)
        except Store.DoesNotExist:
            return Response("No stores for this seller.",
                            status=status.HTTP_404_NOT_FOUND)


class ProductListInStore(APIView):
    permission_classes = [IsAuthenticated]

    def get_products(self, request, store_id, format=None):
        try:
            items = Item.objects.filter(store_id=store_id)
            serializer = ItemSerializer(items, many=True)
            return Response(serializer.data)
        except Item.DoesNotExist:
            return Response("No products in this store.",
                            status=status.HTTP_404_NOT_FOUND)


def view_store_detail(request, store_id):
    store = get_object_or_404(Store, id=store_id)
    items = store.item_set.all()

    return render(request, "shopping_app/store_detail.html", {
        "store": store,
        "items": items,
    })


def store_list(request):
    """View to list all stores."""
    stores = Store.objects.all()
    return render(request, "shopping_app/store_list.html", {"stores": stores})


def send_tweet(message):
    auth = tweepy.OAuth1UserHandler(
        settings.TWITTER_API_KEY,
        settings.TWITTER_API_SECRET,
        settings.TWITTER_ACCESS_TOKEN,
        settings.TWITTER_ACCESS_SECRET,
    )
    api = tweepy.API(auth)
    api.update_status(message)


def twitter_callback(request):
    '''Required in twitter settings to provide a
    callback URL.'''
    return HttpResponse("Twitter callback received.")
