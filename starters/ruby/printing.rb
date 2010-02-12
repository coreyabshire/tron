def puts(*args)
	$stderr.puts *args
end

def p(*args)
	args.map!{|arg| arg.inspect}
	puts args
end

def print(*args)
	$stderr.print *args
end
