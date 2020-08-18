import graphene
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import login_required
from .models import Profile
from graphene_file_upload.scalars import Upload
from graphql import GraphQLError
from django.db import IntegrityError

class  ProfileType(DjangoObjectType):
    class Meta:
        model = Profile
        fields = ("id","name","user")

class Query(graphene.ObjectType):
    profiles = graphene.List(ProfileType)
    profile = graphene.Field(ProfileType, id=graphene.Int(required=True))
    my_profile = graphene.Field(ProfileType)

    @login_required
    def resolve_my_profile(self,info):
        try:
            profile = Profile.objects.get(user=info.context.user)
        except Profile.DoesNotExist:
            raise GraphQLError("You dont have profile")
        return profile

    def resolve_profiles(self,info):
        return Profile.objects.all()
        
    def resolve_profile(self,info,id):
        try:
            profile = Profile.objects.get(id=id)
        except Profile.DoesNotExist:
            raise GraphQLError('Profile with given id doesnt exist')
        return profile
        
class CreateProfile(graphene.Mutation):
    class Arguments:
        file = Upload(required=True)

    profile = graphene.Field(ProfileType)

    @login_required
    def mutate(self, info, file):
        try:
            profile = Profile(name=file[0].name, image=file[0],user=info.context.user)
            profile.save()
        except IntegrityError as err:
            raise GraphQLError("You already have profile image")
        return CreateProfile(profile=profile) 

class DeleteProfile(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    success = graphene.Boolean()

    @login_required
    def mutate(self, info, id):
        try:
            profile = Profile.objects.get(id=id)
        except Profile.DoesNotExist:
            raise GraphQLError('Profile with given id doesnt exist')
        profile.image.delete()
        profile.delete()
        return DeleteProfile(success=True)

class UpdateProfile(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        file = Upload(required=True)
    
    profile = graphene.Field(ProfileType)

    @login_required
    def mutate(self, info,file,id):
        try:
            profile = Profile.objects.get(id=id)
        except Profile.DoesNotExist:
            raise GraphQLError('Profile with given id doesnt exist')
        if profile.user.id is not info.context.user.id:
            raise GraphQLError('You cannot change profile which is not yours')
        profile.image.delete()
        profile.name = file[0].name
        profile.image = file[0]
        profile.save()
        return UpdateProfile(profile=profile)

class Mutation(graphene.ObjectType):
    create_profile = CreateProfile.Field()
    delete_profile = DeleteProfile.Field()
    update_profile = UpdateProfile.Field()