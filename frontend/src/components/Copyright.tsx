import { Box, Typography } from '@mui/material';

export const Copyright = () => {
  return (
    <Box>
      <Typography color="text.secondary">
        Copyright 2024. Junah Kim All right reserved.
      </Typography>
      <Typography color="text.secondary">
        본 서비스는 네이버 주식회사에 의해 운영되지 않습니다. CHZZK은 네이버
        주식회사의 등록된 상표합니다.
      </Typography>
    </Box>
  );
};

export default Copyright;
