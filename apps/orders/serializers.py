from rest_framework import serializers
from .models import CartItem, Order, OrderItem


class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='variant.product.name', read_only=True)
    sku = serializers.CharField(source='variant.sku', read_only=True)
    size = serializers.CharField(source='variant.size', read_only=True)
    color = serializers.CharField(source='variant.color', read_only=True)
    unit_price = serializers.DecimalField(source='variant.price', max_digits=12, decimal_places=2, read_only=True)
    subtotal = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'variant', 'quantity', 'product_name', 'sku', 'size', 'color', 'unit_price', 'subtotal', 'image_url']

    def get_subtotal(self, obj):
        return str(obj.variant.price * obj.quantity)

    def get_image_url(self, obj):
        image = obj.variant.product.images.first()
        return image.image.url if image else None

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError('Quantity must be positive')
        return value

    def validate(self, attrs):
        variant = attrs.get('variant', getattr(self.instance, 'variant', None))
        quantity = attrs.get('quantity', getattr(self.instance, 'quantity', 1))
        if variant and (not variant.active or not variant.product.active or quantity > variant.stock - variant.reserved):
            raise serializers.ValidationError('Variant unavailable or insufficient stock')
        return attrs


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'sku', 'product_name', 'unit_price', 'quantity']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'status', 'subtotal', 'discount', 'total', 'address_snapshot', 'created_at', 'items']


class CheckoutSerializer(serializers.Serializer):
    address_id = serializers.IntegerField(min_value=1)
    coupon_code = serializers.CharField(required=False, allow_blank=True)
