import graphene
from graphene_django import DjangoObjectType
from .models import Review
from graphql_jwt.decorators import login_required
from graphql import GraphQLError
from books.models import Book

class ReviewType(DjangoObjectType):
    class Meta:
        model = Review

class Query(graphene.ObjectType):
    reviews = graphene.List(ReviewType)
    review = graphene.Field(ReviewType, id=graphene.Int(required=True))
    my_reviews = graphene.List(ReviewType)
    book_reviews = graphene.List(ReviewType,book_id=graphene.Int(required=True))

    def resolve_reviews(self, info):
        reviews = Review.objects.all()
        return reviews

    def resolve_review(self,info,id):
        try:
            review = Review.objects.get(id=id)
        except Review.DoesNotExist:
            raise GraphQLError("Review with this id doesn't exist")
        return review

    @login_required
    def resolve_my_reviews(self,info):
        return Review.objects.all().filter(user=info.context.user)

    def resolve_book_reviews(self, info,book_id):
        try:
            book = Book.objects.get(id=book_id)
        except Book.DoesNotExist:
            raise GraphQLError("Book with this id doesn't exist")
        return Review.objects.all().filter(book=book)
class CreateReviewInput(graphene.InputObjectType):
        text = graphene.String(required=True)
        book_id = graphene.Int(required=True)

class CreateReview(graphene.Mutation):
    review = graphene.Field(ReviewType)

    class Arguments:
        create_review_input = CreateReviewInput(required=True)

    @login_required
    def mutate(self, info, create_review_input):
            try:
                book = Book.objects.get(id=create_review_input.book_id)
            except Book.DoesNotExist:
                raise GraphQLError("Book with this id doesn't exist")
            if book.author.id is info.context.user.id:
                 raise GraphQLError("You cannot review your own book")
            review = Review()
            review.book = book
            review.user = info.context.user
            review.save()
            return CreateReview(
                review=review
            )

class UpdateReviewInput(graphene.InputObjectType):
    review_id = graphene.Int(required=True)
    text = graphene.String(required=True)

class UpdateReview(graphene.Mutation):
    review = graphene.Field(ReviewType)
    
    class Arguments:
        update_review_input = UpdateReviewInput(required=True)

    @login_required
    def mutate(self,info,update_review_input):
        try:
            review = Review.objects.get(id=update_review_input.review_id)
        except Review.DoesNotExist:
            raise GraphQLError("Review with this id doesn't exist")
        if review.user.id is not info.context.user.id:
            raise GraphQLError("You cannot update a review which is not yours")
        review.text = update_review_input.text
        review.save()
        return UpdateReview(review=review)

class DeleteReview(graphene.Mutation):
    success = graphene.Boolean()
 
    class Arguments:
        review_id = graphene.Int(required=True)

    def mutate(self,info,review_id):
        try:
            review = Review.objects.get(id=review_id)
        except Book.DoesNotExist:
            raise GraphQLError("Book with this id doesn't exist")
        if review.user.id is not info.context.user.id:
            raise GraphQLError("You cannot delete a review which is not yours")
        review.delete()
        return DeleteReview(success=True)


class Mutation(graphene.ObjectType):
    create_review = CreateReview.Field()
    update_review = UpdateReview.Field()
    delete_review = DeleteReview.Field()
    
