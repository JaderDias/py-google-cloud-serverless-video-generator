output "save_chess_games_url" {
	# Access the module output with module.<module_name>.<output_name>
	value = module.save_chess_games.function_url
}

output "chess_to_script_url" {
	# Access the module output with module.<module_name>.<output_name>
	value = module.chess_to_script.function_url
}