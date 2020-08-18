from django.contrib.auth import get_user_model
import graphene
from graphene_django import DjangoObjectType
from graphql import GraphQLError
from graphql_jwt.decorators import login_required

class UserType(DjangoObjectType):
    class Meta:
        model = get_user_model()
        exclude = ['password']

class Query(graphene.ObjectType):
    users = graphene.List(UserType)
    user = graphene.Field(UserType, id=graphene.Int(required=True))
    me = graphene.Field(UserType)

    @login_required
    def resolve_users(self, info):
        print(info.context.user)
        return get_user_model().objects.all()

    def resolve_user(self,info,id):
        try:
             user = get_user_model().objects.get(id=id)
        except get_user_model().DoesNotExist:
            raise GraphQLError('Cannot find user with given id')
        return user

    def resolve_me(self, info):
        user = info.context.user
        return user
        

class CreateUserInput(graphene.InputObjectType):
    username = graphene.String(required=True)
    password = graphene.String(required=True)
    email = graphene.String(required=True)

class CreateUser(graphene.Mutation):
    user = graphene.Field(UserType)

    class Arguments:
        create_user_input = CreateUserInput(required=True)
    
    def mutate(self,info,create_user_input):
        user =get_user_model()(
            username=create_user_input.username,
            email=create_user_input.email
        )
        user.set_password(create_user_input.password)
        user.save()
        return CreateUser(user=user)

class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()