import graphene
import graphql_jwt
import users.schema
import profiles.schema
import books.schema
import reviews.schema

class Query(users.schema.Query, profiles.schema.Query,books.schema.Query,reviews.schema.Query, graphene.ObjectType):
    pass

class Mutation(users.schema.Mutation,profiles.schema.Mutation,books.schema.Mutation,reviews.schema.Mutation, graphene.ObjectType):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)