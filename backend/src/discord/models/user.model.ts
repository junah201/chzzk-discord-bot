import { Field, Int, ObjectType } from '@nestjs/graphql';

export interface IUser {
  id: string;
  username: string;
  avatar: string;
  discriminator: string;
  public_flags: number;
  premium_type: number;
  flags: number;
  banner: string;
  accent_color: string | null;
  global_name: string;
  banner_color: string | null;
  mfa_enabled: boolean;
  locale: string;
  email: string;
  verified: boolean;
}

@ObjectType()
export class User implements IUser {
  @Field()
  id: string;

  @Field()
  username: string;

  @Field()
  avatar: string;

  @Field()
  discriminator: string;

  @Field(() => Int)
  public_flags: number;

  @Field(() => Int)
  premium_type: number;

  @Field(() => Int)
  flags: number;

  @Field()
  banner: string;

  @Field(() => String, { nullable: true })
  accent_color: string | null;

  @Field()
  global_name: string;

  @Field(() => String, { nullable: true })
  banner_color: string | null;

  @Field(() => Boolean)
  mfa_enabled: boolean;

  @Field()
  locale: string;

  @Field()
  email: string;

  @Field()
  verified: boolean;
}
