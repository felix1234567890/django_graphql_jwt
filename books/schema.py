import graphene
from django.db.models import Q
from graphene_django import DjangoObjectType
from graphql import GraphQLError
from graphql_jwt.decorators import login_required

from .models import Book


class BookType(DjangoObjectType):
    class Meta:
        model = Book

class Query(graphene.ObjectType):
    books = graphene.List(
        BookType,
        search=graphene.String(),
        first=graphene.Int(),
        skip=graphene.Int(),
        description="Get a list of all books, optionally filtered by search term"
    )
    book = graphene.Field(
        BookType,
        id=graphene.Int(required=True),
        description="Get a single book by ID"
    )
    my_books = graphene.List(
        BookType,
        description="Get all books belonging to the authenticated user"
    )

    def resolve_books(self, info, search=None, first=None, skip=None):
        try:
            # Use select_related to optimize queries
            books = Book.objects.select_related('author').all()
            
            if search:
                filter = (
                    Q(title__icontains=search) |
                    Q(description__icontains=search)
                )
                books = books.filter(filter)
            
            if skip and skip < 0:
                raise ValueError("Skip value cannot be negative")
                
            if first and first < 0:
                raise ValueError("First value cannot be negative")
                
            if skip:
                books = books[skip:]
            if first:
                books = books[:first]
                
            return books
            
        except Exception as e:
            raise GraphQLError(str(e))

    def resolve_book(self, info, id):
        try:
            return Book.objects.select_related('author').get(id=id)
        except Book.DoesNotExist:
            raise GraphQLError("Book with this id doesn't exist")
        except Exception as e:
            raise GraphQLError(str(e))

    @login_required
    def resolve_my_books(self, info):
        try:
            return (
                Book.objects
                .select_related('author')
                .filter(author=info.context.user)
                .order_by('-id')  # Latest first
            )
        except Exception as e:
            raise GraphQLError(str(e))

class CreateBookInput(graphene.InputObjectType):
        title = graphene.String(required=True)
        description = graphene.String(required=True)
        year_published = graphene.Int(required=True)

class CreateBook(graphene.Mutation):
    class Arguments:
        create_book_input = CreateBookInput(required=True)

    book = graphene.Field(BookType)
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)

    @login_required
    def mutate(self, info, create_book_input):
        try:
            if create_book_input.year_published < 0:
                return CreateBook(
                    success=False,
                    errors=["Year published cannot be negative"]
                )
                
            book = Book(
                title=create_book_input.title,
                description=create_book_input.description,
                year_published=create_book_input.year_published,
                author=info.context.user
            )
            book.save()
            
            return CreateBook(book=book, success=True)
            
        except Exception as e:
            return CreateBook(
                success=False,
                errors=[str(e)]
            )

class UpdateBookInput(graphene.InputObjectType):
    id = graphene.Int(required=True)
    title = graphene.String()
    description = graphene.String()
    year_published = graphene.Int()

class UpdateBook(graphene.Mutation):
    class Arguments:
        update_book_input = UpdateBookInput(required=True)

    book = graphene.Field(BookType)
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)

    @login_required
    def mutate(self, info, update_book_input):
        try:
            book = Book.objects.get(id=update_book_input.id)
            
            if book.author.id != info.context.user.id:
                return UpdateBook(
                    success=False, 
                    errors=["You cannot update a book which is not yours"]
                )

            if update_book_input.title is not None:
                book.title = update_book_input.title
            if update_book_input.description is not None:
                book.description = update_book_input.description
            if update_book_input.year_published is not None:
                if update_book_input.year_published < 0:
                    return UpdateBook(
                        success=False,
                        errors=["Year published cannot be negative"]
                    )
                book.year_published = update_book_input.year_published
            
            book.save()
            return UpdateBook(book=book, success=True)
            
        except Book.DoesNotExist:
            return UpdateBook(
                success=False,
                errors=["Book with this id doesn't exist"]
            )
        except Exception as e:
            return UpdateBook(
                success=False,
                errors=[str(e)]
            )

class DeleteBook(graphene.Mutation):
    class Arguments:
        book_id = graphene.Int(required=True)

    success = graphene.Boolean()
    errors = graphene.List(graphene.String)

    @login_required
    def mutate(self, info, book_id):
        try:
            book = Book.objects.get(id=book_id)
            
            if book.author.id != info.context.user.id:
                return DeleteBook(
                    success=False,
                    errors=["You cannot delete a book which is not yours"]
                )
                
            book.delete()
            return DeleteBook(success=True)
            
        except Book.DoesNotExist:
            return DeleteBook(
                success=False,
                errors=["Book with this id doesn't exist"]
            )
        except Exception as e:
            return DeleteBook(
                success=False,
                errors=[str(e)]
            )

class Mutation(graphene.ObjectType):
    create_book = CreateBook.Field()
    update_book = UpdateBook.Field()
    delete_book = DeleteBook.Field()

