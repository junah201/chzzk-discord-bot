import { Field, ObjectType, Int } from '@nestjs/graphql';

export interface IChannel {
  id: string;
  type: number;
  last_message_id: string;
  flags: number;
  guild_id: string;
  name: string;
  parent_id: string;
  rate_limit_per_user: number;
  topic: null;
  position: number;
  permission_overwrites: [];
  nsfw: boolean;
}

@ObjectType()
export class Channel implements IChannel {
  @Field()
  id: string;

  @Field(() => Int)
  type: number;

  @Field()
  last_message_id: string;

  @Field(() => Int)
  flags: number;

  @Field()
  guild_id: string;

  @Field()
  name: string;

  @Field()
  parent_id: string;

  @Field(() => Int)
  rate_limit_per_user: number;

  @Field(() => String, { nullable: true })
  topic: null;

  @Field(() => Int)
  position: number;

  @Field(() => [String])
  permission_overwrites: [];

  @Field()
  nsfw: boolean;
}
