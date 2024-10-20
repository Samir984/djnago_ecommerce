from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import api_view, action
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView
from rest_framework.mixins import (
    CreateModelMixin,
    RetrieveModelMixin,
    DestroyModelMixin,
    UpdateModelMixin
)
from rest_framework.permissions import DjangoModelPermissions
from .permission import IsAdminOrReadOnly, FullDjangoModelPermission
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework import status
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count
from rest_framework.pagination import PageNumberPagination
from .models import Product, Collection, Review
from .serializer import (
    ProductSerializer,
    CollectionSerializer,
    ReviewSerializer,
    CartSerializer,
    CartItemSerializer,
    AddCartItemSerializer,
    UpdateCartItemSerializer,
    CustomerSerializer,
    OrderSerializer,
    CreateOrderSerializer,
    UpdateOrderSerializer
)
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from .models import Product, Collection, OrderItem, Cart, CartItem, Customer, Order


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["collection_id", "unit_price"]
    search_fields = ["title", "description"]
    ordering_fields = ["unit_price", "last_update"]
    pagination_class = PageNumberPagination
    permission_classes = [IsAdminOrReadOnly]

    def get_serializer_context(self):
        return {"request": self.request}

    def destroy(self, request, *args, **kwargs):
        if OrderItem.objects.filter(product_id=kwargs["pk"]).count() > 0:
            return Response(
                {
                    "error": "product can't be deleted because it is assocaited with an other item"
                },
                status=status.HTTP_405_METHOD_NOT_ALLOWED,
            )
        return super().destroy(request, *args, **kwargs)


class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.annotate(products_count=Count("products"))
    serializer_class = CollectionSerializer
    permission_classes = [IsAdminOrReadOnly]

    def destroy(self, request, *args, **kwargs):
        collection = get_object_or_404(
            Collection.objects.annotate(products_count=Count("products")),
            pk=kwargs["pk"],
        )
        if collection.products.count() > 0:
            return Response(
                {
                    "error": "Collection can't be deleted because it is assocaited with an other item"
                },
                status=status.HTTP_405_METHOD_NOT_ALLOWED,
            )
        return super().destroy(request, *args, **kwargs)


class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        return Review.objects.filter(product_id=self.kwargs["product_pk"])

    def get_serializer_context(self):
        return {"product_id": self.kwargs["product_pk"]}


class CartViewSet(
    CreateModelMixin, GenericViewSet, RetrieveModelMixin, DestroyModelMixin
):
    queryset = Cart.objects.prefetch_related("items__product").all()
    serializer_class = CartSerializer


class CartItemViewSet(ModelViewSet):
    http_method_names = ["get", "post", "patch", "delete"]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return AddCartItemSerializer

        if self.request.method == "PATCH":
            return UpdateCartItemSerializer
        return CartItemSerializer

    def get_serializer_context(self):
        return {"cart_id": self.kwargs["cart_pk"]}

    def get_queryset(self):
        return CartItem.objects.filter(cart_id=self.kwargs["cart_pk"]).select_related(
            "product"
        )


class CustomerViewSet(ModelViewSet):

    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAdminUser]

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated()]

    @action(detail=False, methods=["GET", "PUT"], permission_classes=[IsAuthenticated])
    def me(self, request):
        print(request.user, "\n\n\n\n")
        (customer, created) = Customer.objects.get_or_create(user_id=request.user.id)
        if request.method == "GET":
            serializer = CustomerSerializer(customer)
            return Response(serializer.data)
        elif request.method == "PUT":
            serializer = CustomerSerializer(customer)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)


class OrderViewSet(ModelViewSet):

    def get_permissions(self):
        if self.request.method in ["PUT","PATCH","DELETE"]:
            return [IsAdminUser()]
        return [IsAuthenticated()]
    
    def create(self, request, *args, **kwargs):
        serializer = CreateOrderSerializer(
            data=request.data, context={"user_id": self.request.user.id}
        )
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CreateOrderSerializer
        elif self.request.method=="PATCH":
            return UpdateOrderSerializer
        return OrderSerializer


    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.all()
        customer_id = Customer.objects.only("id").get(user_id=self.request.user.id)
        return Order.objects.filter(customer_id=customer_id)


# --------------------------------------------------

# def destroy(self, request, pk):
#     collection = get_object_or_404(
#         Collection.objects.annotate(products_count=Count("products")), pk=id
#     )
#     if collection.products.count() > 0:
#         return Response(
#             {
#                 "error": "Collection can't be deleted because it is assocaited with an other item"
#             },
#             status=status.HTTP_405_METHOD_NOT_ALLOWED,
#         )
#     collection.delete()
#     return Response(status=status.HTTP_204_NO_CONTENT)


# class ProductList(ListCreateAPIView):
#     def get_queryset(self):
#        return  Product.objects.all()


#     def get(self,request):
#         queryset = Product.objects.all()
#         serializar = ProductSerializer(queryset, many=True)
#         return Response(serializar.data)

#     def post(self,request):
#         serializar = ProductSerializer(data=request.data)
#         serializar.is_valid(raise_exception=True)
#         print(serializar.validated_data,'\n\n')

#         serializar.save()
#         return Response(serializar.data, status=status.HTTP_201_CREATED)


# class ProductDetail(APIView):
#     def get(self,request):
#      product = get_object_or_404(Product, pk=id)
#      serializar = ProductSerializer(product)
#      return Response(serializar.data)

#     def put(self,id,request):
#       product = get_object_or_404(Product, pk=id)
#       serializar = ProductSerializer(product, data=request.data)
#       serializar.is_valid(raise_exception=True)

#       serializar.save()
#       return Response(serializar.data)

#     def delete(self,id,request):
#        product = get_object_or_404(Product, pk=id)
#        if product.orderitem_set.count() > 0:
#          return Response({"error":"product can't be deleted because it is assocaited with an other item"},status=status.HTTP_405_METHOD_NOT_ALLOWED)
#        product.delete()
#        return Response(status=status.HTTP_204_NO_CONTENT)


# class CollectionList(APIView):

#     def get(self,request):
#         queryset=Collection.objects.annotate(products_count=Count("product"))
#         serializer=CollectionSerializer(queryset)
#         return Response(serializer.data)

#     def post(self,request):
#         serializer=CollectionSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data)


# class CollectionDetail(APIView):
#     def get(self,id,request):
#      collection = get_object_or_404(Collection.objects.annotate(products_count=Count("products")), pk=id)
#      serializar = CollectionSerializer(collection)
#      return Response(serializar.data)

#     def put(self,id,request):
#       collection = get_object_or_404(Collection.objects.annotate(products_count=Count("products")), pk=id)
#       serializar = CollectionSerializer(collection, data=request.data)
#       serializar.is_valid(raise_exception=True)
#       serializar.save()
#       return Response(serializar.data)

#     def delete(self,id,request):
#        collection = get_object_or_404(Collection.objects.annotate(products_count=Count("products")), pk=id)
#        if collection.products.count() > 0:
#          return Response({"error":"Collection can't be deleted because it is assocaited with an other item"},status=status.HTTP_405_METHOD_NOT_ALLOWED)
#        collection.delete()
#        return Response(status=status.HTTP_204_NO_CONTENT)


# def get_queryset(self):
#     queryset=Product.objects.all()
#     collection_id=self.request.query_params.get("collection_id")
#     if collection_id is not None:
#         queryset = queryset.filter(collection_id=collection_id)
