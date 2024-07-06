import { Grid, Box, useTheme, Typography } from '@mui/material';
import { useForm } from 'react-hook-form';

import AddButton from './AddButton';

import { ControlInput } from '@/components/Input';
import { RegisterField, INPUT } from '@/constants/form';
import { Channel } from '@/types';

interface AddFormProps {
  channels: Channel[];
  guildId: string;
}

const AddForm = ({ channels, guildId }: AddFormProps) => {
  const theme = useTheme();

  const { control, handleSubmit } = useForm<RegisterField, any>({
    defaultValues: {
      [INPUT.GUILD_ID.name]: guildId,
      [INPUT.CHZZK_ID.name]: '',
      [INPUT.CHANNEL_ID.name]: null,
      [INPUT.CUSTOM_MESSAGE.name]: '',
      [INPUT.DISABLE_EMBED.name]: false,
      [INPUT.DISABLE_BUTTON.name]: false,
    },
  });

  return (
    <Box
      sx={{
        backgroundColor: theme.palette.background.paper,
        padding: theme.spacing(3),
        display: 'flex',
        flexDirection: 'column',
        gap: theme.spacing(2),
        borderRadius: theme.spacing(1),
      }}
    >
      <Typography variant="h4">치지직 알림 추가</Typography>
      <Grid container gap={3}>
        <Grid item xs={12}>
          <ControlInput
            {...INPUT.CHZZK_ID}
            label="치지직 ID"
            type="text"
            control={control}
            placeholder="bb382c2c0cc9fa7c86"
            helperText="https://chzzk.naver.com/bb382c2c0cc9fa7c86 -> bb382c2c0cc9fa7c86"
          />
        </Grid>
        <Grid item xs={12}>
          <ControlInput
            {...INPUT.CHANNEL_ID}
            label="디스코드 채널"
            type="select"
            control={control}
            placeholder="디스코드 채널을 선택해주세요."
            helperText="알림을 받을 디스코드 채널을 선택해주세요."
            options={channels.map((channel) => ({
              label: `#${channel.name}`,
              value: channel.id,
            }))}
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
          <ControlInput
            {...INPUT.DISABLE_EMBED}
            label="Embed 비활성화"
            type="checkbox"
            control={control}
          />
          <ControlInput
            {...INPUT.DISABLE_BUTTON}
            label="바로가기 버튼 비활성화"
            type="checkbox"
            control={control}
          />
        </Grid>
        <Grid item xs={12}>
          <AddButton handleSubmit={handleSubmit} />
        </Grid>
      </Grid>
    </Box>
  );
};

export default AddForm;
