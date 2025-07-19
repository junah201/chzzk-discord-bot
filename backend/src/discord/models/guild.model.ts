import { Field, ObjectType } from '@nestjs/graphql';

export interface IGuild {
  id: string;
  name: string;
  icon: string;
  owner: boolean;
  permissions: string;
  permissions_new: string;
  features: string[];
}

@ObjectType()
export class Guild implements IGuild {
  @Field()
  id: string;

  @Field()
  name: string;

  @Field()
  icon: string;

  @Field()
  owner: boolean;

  @Field()
  permissions: string;

  @Field()
  permissions_new: string;

  @Field(() => [String])
  features: string[];
}
