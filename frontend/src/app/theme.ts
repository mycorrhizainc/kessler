import { Theme, extendTheme, type ThemeConfig } from "@chakra-ui/react";
import { theme as baseTheme } from "@saas-ui/react";

const colors = {
  "black": "#061e10",
  "gray": {
    "50": "#f9faf9",
    "100": "#eff2f0",
    "200": "#e4e8e6",
    "300": "#ced6d1",
    "400": "#a1b0a7",
    "500": "#6c8576",
    "600": "#3a5c48",
    "700": "#173e27",
    "800": "#082514",
    "900": "#061e10",
  },
  "green": {
    "50": "#f5fdfa",
    "100": "#cbf4e2",
    "200": "#90e7c1",
    "300": "#43d696",
    "400": "#17be76",
    "500": "#14a365",
    "600": "#108754",
    "700": "#0d6941",
    "800": "#0b5635",
    "900": "#09472c",
  },
  "teal": {
    "50": "#f2fcfc",
    "100": "#c6f0f3",
    "200": "#93e2e7",
    "300": "#4ecfd8",
    "400": "#17b2bd",
    "500": "#1497a1",
    "600": "#107b83",
    "700": "#0c6066",
    "800": "#0a5055",
    "900": "#084246",
  },
  "cyan": {
    "50": "#f5fbfd",
    "100": "#d4eef6",
    "200": "#c0e6f1",
    "300": "#a9ddec",
    "400": "#63c1dd",
    "500": "#40b3d5",
    "600": "#19a1cb",
    "700": "#1486a8",
    "800": "#116e8a",
    "900": "#0d556b",
  },
  "blue": {
    "50": "#f2f6fc",
    "100": "#cfdff5",
    "200": "#acc8ed",
    "300": "#85aee4",
    "400": "#6096dc",
    "500": "#3e7fd5",
    "600": "#1967cd",
    "700": "#134f9d",
    "800": "#104181",
    "900": "#0d3569",
  },
  "purple": {
    "50": "#f9f6fd",
    "100": "#e5daf7",
    "200": "#d3bef1",
    "300": "#b796e8",
    "400": "#a47ae2",
    "500": "#8954da",
    "600": "#7637d4",
    "700": "#6019cb",
    "800": "#4f14a8",
    "900": "#3b0f7e",
  },
  "pink": {
    "50": "#fdf5f9",
    "100": "#f7d9e6",
    "200": "#f0bad2",
    "300": "#e790b5",
    "400": "#e070a0",
    "500": "#d64181",
    "600": "#c91965",
    "700": "#a51453",
    "800": "#811041",
    "900": "#600c30",
  },
  "red": {
    "50": "#fdf6f5",
    "100": "#f6dad8",
    "200": "#efb8b5",
    "300": "#e58f88",
    "400": "#df756e",
    "500": "#d74f45",
    "600": "#cc2519",
    "700": "#a51e14",
    "800": "#8c1911",
    "900": "#67130d",
  },
  "orange": {
    "50": "#fdfaf6",
    "100": "#f7ebdc",
    "200": "#efd5b3",
    "300": "#e2b478",
    "400": "#d69541",
    "500": "#c57a18",
    "600": "#a76714",
    "700": "#855210",
    "800": "#69410d",
    "900": "#56350a",
  },
  "yellow": {
    "50": "#fefefc",
    "100": "#fbf9ec",
    "200": "#f3eec7",
    "300": "#e9e19b",
    "400": "#dbce5a",
    "500": "#baa917",
    "600": "#948712",
    "700": "#746a0e",
    "800": "#574f0b",
    "900": "#484109",
  },
  "primary": {
    "50": "#edfbee",
    "100": "#b3efb8",
    "200": "#66de70",
    "300": "#17c025",
    "400": "#15ac21",
    "500": "#12911c",
    "600": "#0f7a17",
    "700": "#0c6213",
    "800": "#0a5310",
    "900": "#073c0b",
  },
};

const config = {
  colors: {
    ...colors,
  },
  initialColorMode: 'dark'
}

const theme = extendTheme(
  {
    config
  },
  baseTheme
);



export default theme;
