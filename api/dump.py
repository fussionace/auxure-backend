
# The modified view function to also fetch similar perfumes and display on the perfume detail page
# Viewset for Perfumes GRID VIEW
class PerfumesViewSet(ModelViewSet):
    queryset = Perfume.objects.all()
    serializer_class = PerfumeSerializer
    permission_classes = [permissions.IsAdminOrReadOnly] # Inheriting custom permission

    # Implementing filter and search
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = PerfumeFilter
    search_fields = ['name', 'description']
    ordering_fields = ['price']     #You can order by any other field or add other fields
    # Implementing Pagination - Not necessary except to overide the setting in the restframework dictionary
    # pagination_class = PageNumberPagination
    # page_size = 3

    @extend_schema(responses=CategorySerializer)
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        # Fetch similar perfumes based on title and gender
        similar_perfumes = Perfume.objects.filter(
            category__title=instance.category.title,
            category__gender=instance.category.gender,
            price__lte=instance.price + 50,   #Defining the price range
            price__gte=instance.price - 50
        ).exclude(id=instance.id)

        similar_perfume_serializer = PerfumeSerializer(similar_perfumes, many=True)

        # Combine the perfume details and similar perfumes in the response
        response_data = {
            'perfume': serializer.data,
            'similar_perfumes': similar_perfume_serializer.data
        }

        return Response(response_data)
    

    


# Viewset for Perfumes LIST VIEW
class CustomListViewPagination(PageNumberPagination):
    page_size = 4

class ListViewSet(ModelViewSet):
    queryset = Perfume.objects.all()
    serializer_class = PerfumeSerializer
    permission_classes = [permissions.IsAdminOrReadOnly] # Inheriting custom permission

    # Implementing filter and search
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = PerfumeFilter
    search_fields = ['name', 'description']
    ordering_fields = ['price']

    def get_queryset(self):
        # Set custom pagination class before executing the queryset
        self.pagination_class = CustomListViewPagination
        return Perfume.objects.all()
    
    @extend_schema(responses=CategorySerializer)
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        # Fetch similar perfumes based on title and gender
        similar_perfumes = Perfume.objects.filter(
            category__title=instance.category.title,
            category__gender=instance.category.gender,
            price__lte=instance.price + 50,   #Defining the price range
            price__gte=instance.price - 50
        ).exclude(id=instance.id)

        similar_perfume_serializer = PerfumeSerializer(similar_perfumes, many=True)

        # Combine the perfume details and similar perfumes in the response
        response_data = {
            'perfume': serializer.data,
            'similar_perfumes': similar_perfume_serializer.data
        }

        return Response(response_data)