import { DynamoDBClient } from '@aws-sdk/client-dynamodb';
import { DynamoDBDocumentClient, PutCommand } from '@aws-sdk/lib-dynamodb';
import { Injectable } from '@nestjs/common';

@Injectable()
export class DynamodbService {
  private client = new DynamoDBClient({ region: 'ap-northeast-2' });
  public docClient = DynamoDBDocumentClient.from(this.client);
  public readonly tableName = 'chzzk-bot-db';
  public readonly guidIdPkIndex = 'GSI-GuildID';
  public readonly indexPkIndex = 'GSI-Index';
  public readonly SKPKIndex = 'GSI-SK';
  public readonly typeIndex = 'GSI-type';

  constructor() {
    const client = new DynamoDBClient({
      region: 'ap-northeast-2',
    });

    this.docClient = DynamoDBDocumentClient.from(client, {});
  }

  public async put(item: Record<string, any>): Promise<void> {
    await this.docClient.send(
      new PutCommand({
        TableName: this.tableName,
        Item: this.normalizeItem(item),
      }),
    );
  }

  public normalizeItem(obj: any): any {
    if (Array.isArray(obj)) {
      return obj.map(this.normalizeItem);
    }
    if (typeof obj === 'object' && obj !== null) {
      return Object.fromEntries(
        Object.entries(obj).map(([k, v]) => [k, this.normalizeItem(v)]),
      );
    }
    return obj;
  }
}
