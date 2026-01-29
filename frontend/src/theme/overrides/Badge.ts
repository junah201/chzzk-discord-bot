import { ThemeOptions } from "../types";

export default function Badge(theme: ThemeOptions) {
	return {
		MuiBadge: {
			styleOverrides: {
				standard: {
					minWidth: theme.spacing(2),
					height: theme.spacing(2),
					padding: theme.spacing(0.5),
				},
			},
		},
	};
}
