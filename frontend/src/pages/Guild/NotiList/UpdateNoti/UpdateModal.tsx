import { Grid } from '@mui/material';
import { useForm } from 'react-hook-form';

import UpdateButton from './UpdateButton';

import { ControlInput } from '@/components/Input';
import { RegisterField, INPUT } from '@/constants/form';
import { Notification } from '@/types';

interface DetailModalProps {
  noti: Notification;
}

const DetailModal = ({ noti }: DetailModalProps) => {
  const { control, handleSubmit } = useForm<RegisterField, any>({
    defaultValues: {
      [INPUT.CHZZK_ID.name]: noti.PK.split('#')[1],
      [INPUT.CHANNEL_ID.name]: noti.channel_id,
      [INPUT.CUSTOM_MESSAGE.name]: noti.custom_message,
    },
  });

  return (
    <Grid
      container
      gap={3}
      sx={{
        mt: 1,
      }}
    >
      <Grid item xs={12}>
        <ControlInput
          {...INPUT.CHZZK_ID}
          label="치지직 ID"
          type="text"
          control={control}
          placeholder="bb382c2c0cc9fa7c86"
          helperText="https://chzzk.naver.com/bb382c2c0cc9fa7c86 -> bb382c2c0cc9fa7c86"
          disabled={true}
        />
      </Grid>
      <Grid item xs={12}>
        <ControlInput
          {...INPUT.CHANNEL_ID}
          label="디스코드 채널"
          type="text"
          control={control}
          placeholder="디스코드 채널을 선택해주세요."
          helperText="알림을 받을 디스코드 채널을 선택해주세요."
          options={[
            {
              label: `#${noti.channel_name}`,
              value: noti.channel_id,
            },
          ]}
          disabled={true}
        />
      </Grid>
      <Grid item xs={12}>
        <ControlInput
          {...INPUT.CUSTOM_MESSAGE}
          label="커스텀 메시지"
          type="multiline"
          control={control}
          placeholder="@everyone 홍길동님이 방송을 시작했습니다!"
          helperText="알림에 커스텀 메시지를 추가할 수 있습니다."
        />
      </Grid>
      <Grid item xs={12}>
        <UpdateButton handleSubmit={handleSubmit} />
      </Grid>
    </Grid>
  );
};

export default DetailModal;
