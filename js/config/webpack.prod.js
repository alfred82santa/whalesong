const webpack = require('webpack');
const path = require('path');
const TerserPlugin = require('terser-webpack-plugin');

/*
 * SplitChunksPlugin is enabled by default and replaced
 * deprecated CommonsChunkPlugin. It automatically identifies modules which
 * should be splitted of chunk by heuristics using module duplication count and
 * module category (i. e. node_modules). And splits the chunks…
 *
 * It is safe to remove "splitChunks" from the generated configuration
 * and was added as an educational example.
 *
 * https://webpack.js.org/plugins/split-chunks-plugin/
 *
 */

module.exports = {
	module: {
		rules: [
			{
				test: /\.js$/,
				include: [path.resolve(__dirname, '../src')],
				loader: 'babel-loader',

				options: {
					presets: [
						'env'
					],

					plugins: [
						'syntax-dynamic-import',
						'transform-decorators-legacy',
						"syntax-class-properties",
						["transform-runtime", {
                          "polyfill": true,
                          "regenerator": true
                        }]

				  ]
				}
			}
		]
	},

	mode: 'production',

	output: {
		jsonpFunction: "webpackJsonpWhalesong"
	},

	optimization: {
	    minimizer: [
	        new TerserPlugin({
	            test: /\.js(\?.*)?$/i,
	            terserOptions: {
	                keep_classnames: true,
                    keep_fnames: true
	            }
	        })
	    ]
	}
};
