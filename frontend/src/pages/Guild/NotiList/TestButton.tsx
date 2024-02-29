import { MailOutlined } from '@mui/icons-material';
import { IconButton, Tooltip } from '@mui/material';

import { sendTestNotification } from '@/api';
import { useCustomMutation } from '@/lib';

interface TestButtonProps {
  channel_id: string;
  chzzk_id: string;
}

const TestButton = ({ channel_id, chzzk_id }: TestButtonProps) => {
  const { mutate, isLoading } = useCustomMutation(
    () =>
      sendTestNotification({
        channel_id,
        chzzk_id,
      }),
    {
      SuccessMessage: `테스트 알림이 전송되었습니다.`,
      ErrorMessage: '',
    }
  );

  return (
    <Tooltip title="테스트 알림 전송" placement="top" arrow>
      <span>
        <IconButton onClick={mutate} disabled={isLoading}>
          <MailOutlined color="secondary" />
        </IconButton>
      </span>
    </Tooltip>
  );
};

export default TestButton;
