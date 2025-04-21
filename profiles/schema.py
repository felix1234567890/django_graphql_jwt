import graphene
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from graphene_django import DjangoObjectType
from graphene_file_upload.scalars import Upload
from graphql import GraphQLError
from graphql_jwt.decorators import login_required

from .models import Profile


class  ProfileType(DjangoObjectType):
    class Meta:
        model = Profile
        fields = ("id","name","user")

class Query(graphene.ObjectType):
    profiles = graphene.List(ProfileType)
    profile = graphene.Field(ProfileType, id=graphene.Int(required=True))
    my_profile = graphene.Field(ProfileType)

    def resolve_profiles(self, info):
        try:
            return Profile.objects.all()
        except Exception as e:
            raise GraphQLError(f'Failed to fetch profiles: {str(e)}')

    def resolve_profile(self, info, id):
        try:
            return Profile.objects.get(id=id)
        except Profile.DoesNotExist:
            raise GraphQLError('Profile with given ID does not exist')
        except Exception as e:
            raise GraphQLError(f'Failed to fetch profile: {str(e)}')

    @login_required
    def resolve_my_profile(self, info):
        try:
            return Profile.objects.get(user=info.context.user)
        except Profile.DoesNotExist:
            raise GraphQLError('You do not have a profile')
        except Exception as e:
            raise GraphQLError(f'Failed to fetch your profile: {str(e)}')

class CreateProfile(graphene.Mutation):
    class Arguments:
        file = Upload(required=True)

    profile = graphene.Field(ProfileType)
    success = graphene.Boolean()

    @login_required
    def mutate(self, info, file):
        if not file:
            raise GraphQLError('No file was uploaded')
            
        try:
            # Check if user already has a profile
            if Profile.objects.filter(user=info.context.user).exists():
                raise GraphQLError('You already have a profile')
                
            profile = Profile(
                name=file[0].name,
                image=file[0],
                user=info.context.user
            )
            
            try:
                profile.full_clean()  # Validate the model
                profile.save()
                return CreateProfile(profile=profile, success=True)
                
            except ValidationError as e:
                raise GraphQLError(str(e))
                
        except Exception as e:
            raise GraphQLError(f'Failed to create profile: {str(e)}')

class DeleteProfile(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    success = graphene.Boolean()

    @login_required
    def mutate(self, info, id):
        try:
            profile = Profile.objects.get(id=id)
            
            # Check permissions
            if profile.user.id != info.context.user.id:
                raise GraphQLError('You cannot delete a profile that is not yours')
            
            # Delete image first
            if profile.image:
                profile.image.delete()
                
            profile.delete()
            return DeleteProfile(success=True)
            
        except Profile.DoesNotExist:
            raise GraphQLError('Profile with given ID does not exist')
        except Exception as e:
            raise GraphQLError(f'Failed to delete profile: {str(e)}')

class UpdateProfile(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        file = Upload(required=True)
    
    profile = graphene.Field(ProfileType)
    success = graphene.Boolean()

    @login_required
    def mutate(self, info, file, id):
        if not file:
            raise GraphQLError('No file was uploaded')
            
        try:
            profile = Profile.objects.get(id=id)
            
            # Check permissions first
            if profile.user.id != info.context.user.id:
                raise GraphQLError('You cannot modify a profile that is not yours')
                
            # Save old image reference for cleanup
            old_image = profile.image
            
            # Update profile
            profile.name = file[0].name
            profile.image = file[0]
            
            try:
                profile.full_clean()  # Validate the model
                profile.save()
                
                # Only delete old image after successful save
                if old_image:
                    old_image.delete()
                    
                return UpdateProfile(profile=profile, success=True)
                
            except ValidationError as e:
                raise GraphQLError(str(e))
                
        except Profile.DoesNotExist:
            raise GraphQLError('Profile with the given ID does not exist')
        except Exception as e:
            raise GraphQLError(f'Failed to update profile: {str(e)}')

class Mutation(graphene.ObjectType):
    create_profile = CreateProfile.Field()
    delete_profile = DeleteProfile.Field()
    update_profile = UpdateProfile.Field()