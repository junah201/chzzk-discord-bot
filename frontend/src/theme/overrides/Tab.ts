import { ThemeOptions } from "../types";

export default function Tab(theme: ThemeOptions) {
	return {
		MuiTab: {
			styleOverrides: {
				root: {
					minHeight: 46,
					color: theme.palette.text.primary,
				},
			},
		},
	};
}
