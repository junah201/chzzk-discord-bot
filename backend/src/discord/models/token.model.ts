import { Field, ObjectType } from '@nestjs/graphql';

export interface IToken {
  code: string;
}

@ObjectType()
export class Token implements IToken {
  @Field()
  code: string;
}
