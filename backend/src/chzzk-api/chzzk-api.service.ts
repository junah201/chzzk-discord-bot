import { GetCommand } from '@aws-sdk/lib-dynamodb';
import {
  BadRequestException,
  Injectable,
  Logger,
  NotFoundException,
} from '@nestjs/common';

import { AxiosService } from '@/common/axios/axios.service';
import { DynamodbService } from '@/common/dynamodb/dynamodb.service';

import { ChzzkAccount } from './interface/chzzk-account.interface';
import { ChzzkLive } from './interface/chzzk-live.interface';

@Injectable()
export class ChzzkAPIService {
  private readonly MAX_RETRIES = 2;

  constructor(
    private readonly axiosService: AxiosService,
    private readonly dynamodbService: DynamodbService,
    private readonly logger: Logger,
  ) {}

  async getChzzk(chzzkId: string) {
    if (chzzkId.includes('/')) {
      this.logger.error('Invalid chzzk channel id', {
        type: 'INVALID_CHZZK_CHANNEL_ID',
        channelId: chzzkId,
        func: this.getChzzk.name,
      });

      throw new NotFoundException(
        `치지직 채널(id=${chzzkId})을 찾을 수 없습니다.`,
      );
    }

    for (let attempt = 1; attempt <= this.MAX_RETRIES; attempt++) {
      try {
        const res = await this.axiosService.get(
          'chzzk',
          `/channels/${chzzkId}/live-detail`,
          {
            'User-Agent':
              'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.87 Safari/537.36',
          },
        );

        if (res.status !== 200) {
          this.logger.error('Invalid chzzk response', {
            type: 'INVALID_RESPONSE',
            channelId: chzzkId,
            statusCode: res.status,
            response: res.data,
            func: this.getChzzk.name,
          });
          throw new NotFoundException(
            `치지직 채널(id=${chzzkId})을 찾을 수 없습니다.`,
          );
        }

        const content = res.data?.content;

        if (!content) {
          throw new NotFoundException(
            `치지직 채널(id=${chzzkId})을 찾을 수 없습니다.`,
          );
        }

        return content as ChzzkLive;
      } catch (error) {
        this.logger.error('Failed to fetch chzzk live detail', {
          type: 'CHZZK_REQUEST_ERROR',
          channelId: chzzkId,
          attempt,
          exception: error,
          func: this.getChzzk.name,
        });

        throw new NotFoundException(
          `치지직 채널(id=${chzzkId})을 찾을 수 없습니다.`,
        );
      }
    }
    throw new NotFoundException(
      `치지직 채널(id=${chzzkId})을 찾을 수 없습니다.`,
    );
  }

  async followChannel(index: number, chzzkId: string) {
    const accountRes = await this.dynamodbService.docClient.send(
      new GetCommand({
        TableName: this.dynamodbService.tableName,
        Key: {
          PK: `NAVER#${index}`,
          SK: `NAVER#${index}`,
        },
      }),
    );

    if (!accountRes.Item) {
      this.logger.error('NAVER_ACCOUNT_NOT_FOUND', {
        index,
        chzzkId,
        func: this.followChannel.name,
      });
      throw new NotFoundException(
        `네이버 계정(index=${index})을 찾을 수 없습니다.`,
      );
    }

    const naverAccount = accountRes.Item as ChzzkAccount;
    const { NID_AUT, NID_SES } = naverAccount;

    const followingRes = await this.axiosService.post(
      'chzzk',
      `/channels/${chzzkId}/follow`,
      {},
      {
        'User-Agent':
          'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.87 Safari/537.36',
        Cookie: `NID_AUT=${NID_AUT}; NID_SES=${NID_SES}`,
      },
    );

    if (followingRes.status !== 200) {
      this.logger.error('CHZZK_FOLLOW_ERROR', {
        chzzkId,
        statusCode: followingRes.status,
        response: followingRes.data,
        func: this.followChannel.name,
      });
      throw new BadRequestException(
        `치지직 채널(id=${chzzkId}) 팔로우에 실패했습니다. 다시 시도해주세요.`,
      );
    }
  }
}
