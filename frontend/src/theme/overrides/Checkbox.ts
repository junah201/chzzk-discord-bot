import { ThemeOptions } from "../types";

export default function Checkbox(theme: ThemeOptions) {
	return {
		MuiCheckbox: {
			styleOverrides: {
				root: {
					color: theme.palette.secondary.light,
				},
			},
		},
	};
}
