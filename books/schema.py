import graphene
from graphene_django import DjangoObjectType
from .models import Book
from django.db.models import Q
from graphql_jwt.decorators import login_required
from graphql import GraphQLError

class BookType(DjangoObjectType):
    class Meta:
        model = Book

class Query(graphene.ObjectType):
    books = graphene.List(BookType, 
    search=graphene.String(), first = graphene.Int(), skip=graphene.Int())
    book = graphene.Field(BookType, id=graphene.Int(required=True))
    my_books = graphene.List(BookType)

    def resolve_books(self, info, search=None, first=None, skip=None):
        books = Book.objects.all()
        if search:
            filter = Q(title__icontains=search) 
            books = books.filter(filter)
        if skip:
            books = books[skip:]
        if first:
            books = books[:first]
        return books

    def resolve_book(self,info,id):
        try:
            book = Book.objects.get(id=id)
        except Book.DoesNotExist:
            raise GraphQLError("Book with this id doesn't exist")
        return book

    @login_required
    def resolve_my_books(self,info):
        return Book.objects.all().filter(author=info.context.user)

class CreateBookInput(graphene.InputObjectType):
        title = graphene.String(required=True)
        description = graphene.String(required=True)
        year_published = graphene.Int(required=True)

class CreateBook(graphene.Mutation):
    book = graphene.Field(BookType)

    class Arguments:
        create_book_input = CreateBookInput(required=True)

    @login_required
    def mutate(self, info, create_book_input):
            book = Book()
            book.title = create_book_input.title
            book.description = create_book_input.description
            book.year_published = create_book_input.year_published
            book.author = info.context.user
            book.save()
            return CreateBook(
                book=book
            )

class UpdateBookInput(graphene.InputObjectType):
    id = graphene.Int(required=True)
    title = graphene.String()
    description = graphene.String()
    year_published = graphene.Int()

class UpdateBook(graphene.Mutation):
    book = graphene.Field(BookType)
    
    class Arguments:
        update_book_input = UpdateBookInput(required=True)

    @login_required
    def mutate(self,info,update_book_input):
        try:
            book = Book.objects.get(id=update_book_input.id)
        except Book.DoesNotExist:
            raise GraphQLError("Book with this id doesn't exist")
        if book.author.id is not info.context.user.id:
            raise GraphQLError("You cannot update a book which is not yours")
        if update_book_input.title is not None:
            book.title = update_book_input.title
        if update_book_input.description is not None:
            book.description = update_book_input.description
        if update_book_input.year_published is not None:
            book.year_published = update_book_input.year_published
        book.save()
        return UpdateBook(book=book)

class DeleteBook(graphene.Mutation):
    success= graphene.Boolean()

    class Arguments:
        book_id = graphene.Int(required=True)

    def mutate(self,info,book_id):
        try:
            book = Book.objects.get(id=book_id)
        except Book.DoesNotExist:
            raise GraphQLError("Book with this id doesn't exist")
        if book.author.id is not info.context.user.id:
            raise GraphQLError("You cannot delete a book which is not yours")
        book.delete()
        return DeleteBook(success=True)


class Mutation(graphene.ObjectType):
    create_book = CreateBook.Field()
    update_book = UpdateBook.Field()
    delete_book = DeleteBook.Field()
    
