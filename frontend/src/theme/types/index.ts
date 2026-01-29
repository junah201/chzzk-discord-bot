import { Theme as MuiTheme, Palette as MuiPalette } from "@mui/material/styles";

interface PaletteColorOptions {
	lighter: string;
	50: string;
	100: string;
	200: string;
	300: string;
	light: string;
	400: string;
	500: string;
	main: string;
	dark: string;
	600: string;
	700: string;
	800: string;
	darker: string;
	900: string;
	A50: string;
	A100: string;
	A200: string;
	A300: string;
	A400: string;
	A700: string;
	A800: string;
	contrastText: string;
}

interface Palettes extends MuiPalette {
	primary: PaletteColorOptions;
	secondary: PaletteColorOptions;
	error: PaletteColorOptions;
	warning: PaletteColorOptions;
	info: PaletteColorOptions;
	success: PaletteColorOptions;
	grey: PaletteColorOptions;
}

interface Shadows {
	button: string;
	text: string;
	z1: string;
}

export interface ThemeOptions extends MuiTheme {
	customShadows: Shadows;
	palette: Palettes;
}
