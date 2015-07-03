// Percent the second texture shows
uniform sampler2D TextureUnit1;

void main (void)
{
	vec4 first = texture2D( TextureUnit1, gl_TexCoord[0].st);

	gl_FragColor = first;//vec4(1,0,0,1);
}