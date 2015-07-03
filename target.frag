// center position of cone
uniform float PointerX;
uniform sampler2D TextureUnit1;

void main (void)
{
	// get texture color at that fragment
	vec4 first = texture2D( TextureUnit1, gl_TexCoord[0].st);
	// if there's no texture, use its color
	if(first.x == 0.0 && first.y == 0.0 && first.z == 0.0)
		first = gl_Color;
	// make it really red
	gl_FragColor = first * vec4(1.0,0.0,0.0,1.0);
}