import { Box, Typography } from '@mui/material';
import { Link } from 'react-router-dom';

interface PageButtonProps {
  nextPath?: string;
  nextText?: string;
  prevPath?: string;
  prevText?: string;
}

export const PageButton = ({
  nextPath,
  nextText,
  prevPath,
  prevText,
}: PageButtonProps) => {
  return (
    <Box
      display="flex"
      flexDirection="column"
      paddingY="24px"
      marginY="24px"
      sx={{
        borderTop: '1px solid',
        borderBottom: '1px solid',
      }}
    >
      <Box display="flex" justifyContent="space-between">
        <Box width="48%">
          {prevPath && (
            <Box
              component={Link}
              to={prevPath}
              sx={{
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'flex-end',
                width: '100%',
                border: '1px solid',
                textAlign: 'left',
                padding: '12px',
                borderRadius: '8px',
                transition: 'border-color .25s',
                '&:hover': {
                  borderColor: 'primary.main',
                },
              }}
            >
              <Typography>이전 페이지</Typography>
              <Typography color="primary.main" fontWeight="bold">
                {prevText}
              </Typography>
            </Box>
          )}
        </Box>
        <Box width="48%">
          {nextPath && (
            <Box
              component={Link}
              to={nextPath}
              sx={{
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'flex-end',
                width: '100%',
                border: '1px solid',
                textAlign: 'right',
                padding: '12px',
                borderRadius: '8px',
                transition: 'border-color .25s',
                '&:hover': {
                  borderColor: 'primary.main',
                },
              }}
            >
              <Typography>다음 페이지</Typography>
              <Typography color="primary.main" fontWeight="bold">
                {nextText}
              </Typography>
            </Box>
          )}
        </Box>
      </Box>
    </Box>
  );
};

export default PageButton;
