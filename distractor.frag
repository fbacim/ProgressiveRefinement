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
	// then, reduce r,g,b by 0.5
	float grayscale = .2126 * first.x + .7152 * first.y + .0722 * first.z;
	first = vec4(grayscale,grayscale,grayscale,1.0);
	gl_FragColor = clamp(first - vec4(0.5,0.5,0.5,0.0), 0.0, 1.0);
}