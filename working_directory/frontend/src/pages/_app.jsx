import { ChakraProvider } from '@chakra-ui/react';
import { theme as proTheme } from '@chakra-ui/pro-theme'
import { extendTheme, theme as baseTheme } from '@chakra-ui/react'
import { MadeWithSGBadge } from '@components/MadeWithSGBadge'

export const theme = extendTheme(
  {
    colors: { ...baseTheme.colors, brand: baseTheme.colors.blue },
  },
  proTheme,
)

export default function App({ Component, pageProps }) {
  return (
    <ChakraProvider theme={theme}>
      <Component {...pageProps} />
      <MadeWithSGBadge/>
    </ChakraProvider>
  );
}